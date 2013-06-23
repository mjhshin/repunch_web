////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("assign_punch_code", function(request, response) {
    var PunchCode = Parse.Object.extend("PunchCode");
    var query = new Parse.Query(PunchCode);
    query.equalTo("is_taken", false);
    query.first({
        success: function(object) {
            // The object was retrieved successfully.
            object.set("is_taken", true);
            object.set("username", request.params.username);
                       
            object.save(null, {
                success: function(object) {
                    // The object was saved successfully.
                    response.success( object.get("punch_code") );
                },
                error: function(object, error) {
                    // The save failed.
                    response.error("Error: " + error.code + " " + error.message);
                }
            });
        },
        error: function(error) {
            // The object was not retrieved successfully.
            response.error("Error: " + error.code + " " + error.message);
        }
    });
});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("punch", function(request, response) {
    var punchCode = request.params.punch_code;
	var numPunches = request.params.num_punches;
	var storeId = request.params.store_id;
	var storeName = request.params.store_name;
	var employeeId = request.params.employee_id;
   
	var Patron = Parse.Object.extend("Patron");
	var patron = new Patron();
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var Employee = Parse.Object.extend("Employee");
   
	var patronQuery = new Parse.Query(Patron);
	var patronStoreQuery = new Parse.Query(PatronStore);
	var storeQuery = new Parse.Query(Store);
	var installationQuery = new Parse.Query(Parse.Installation);
   
	patronQuery.equalTo("punch_code", punchCode);
	storeQuery.equalTo("objectId", storeId);
	patronStoreQuery.matchesQuery("Patron", patronQuery);
	patronStoreQuery.matchesQuery("Store", storeQuery);
	patronStoreQuery.include("Patron");
	patronStoreQuery.include("Store");
	installationQuery.equalTo("punch_code", punchCode);
				   
	patronStoreQuery.first({
		success: function(patronStoreResult) {
			if(patronStoreResult == null) {//customer's first punch at this store, need new PatronStore.
				addPatronStore();				
			} else {
				updatePatronStore(patronStoreResult);
			}
		},
		error: function(error) {
			console.log("PatronStore query failed.");
			response.error("error");
		}
	});
	
	function addPatronStore() {
		console.log("customer's first punch at this store, adding new PatronStore.");
		var patronStore = new PatronStore();
		patronStore.set("punch_count", numPunches);
		patronStore.set("all_time_punches", numPunches);
								  
		patronQuery.first().then(function(patronResult) { //get Patron
			console.log("Patron fetched");
			patron = patronResult;
			patronStore.set("Patron", patronResult);
			return storeQuery.first();
			
		}, function(error) {
			console.log("Store query failed.");
			response.error("error");	
			
		}).then(function(storeResult) { //get Store
			console.log("Store fetched");
			patronStore.set("Store", storeResult);
			return patronStore.save();
			
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
			
		}).then(function(patronStore) { // save PatronStore
			console.log("saved PatronStore");
			patron.relation("PatronStores").add(patronStore);
			return patron.save();
			
		}, function(error) {
			console.log("Patron save failed.");
			response.error("error");
			
		}).then(function() {// save Patron 
			console.log("saved Patron");
			executePush();
			saveDataForAnalytics(patronStore, true);
			
		});
	}
	
	function updatePatronStore(patronStoreResult) {
		console.log("updating existing PatronStore");
		patronStoreResult.increment("punch_count", numPunches);
		patronStoreResult.increment("all_time_punches", numPunches);
		patron = patronStoreResult.get("Patron");
		patronStoreResult.save().then(function(patronStoreResult) {
			console.log("PatronStore save was successful.");
			executePush();
			saveDataForAnalytics(patronStoreResult, false);
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
		});
	}
	
	function executePush() {
		Parse.Push.send({
			where: installationQuery,
			data: {
				name: storeName,
				id: storeId,
				num_punches: numPunches,
				action: "com.repunch.intent.PUNCH"
			}
		}, {
			success: function() {
				console.log("push was successful");
			},
			error: function(error) {
				response.error("error");
			}
		});
	}
	
	function saveDataForAnalytics(patronStore, isNewPatronStore) {
		var Punch = Parse.Object.extend("Punch");
		var punch = new Punch();
		
		punch.set("Patron", patronStore.get("Patron"));
		punch.set("punches", numPunches);
		punch.save().then(function(punch) {
			console.log("Punch save was successful.");
			var store = new Store();
			store = patronStore.get("Store");
			store.relation("Punches").add(punch);
			
			if(isNewPatronStore) {
				store.relation("PatronStores").add(patronStore);
			}
			
			return store.save();
			
		}, function(error) {
				console.log("Store save failed.");
				response.error("error");
				
		}).then(function(store) {
				console.log("Store save was successful.");
				
				if(employeeId != null) {
					var employeeQuery = new Parse.Query(Employee);
					return employeeQuery.get(employeeId);
				} else {
					console.log("Employee ID is null, punch was from dashboard.");
				}
						
		}, function(error) {
				console.log("Employee fetch failed.");
				response.error("error");	
				
		}).then(function(employee) {
				if(employeeId != null) {
					console.log("Employee fetched.");
					employee.relation("Punches").add(punch);
					employee.increment("lifetime_punches", numPunches);
					return employee.save();
				}
				
		}, function(error) {
				console.log("Employee save failed.");
				response.error("error");	
				
		}).then(function(employee) {
				console.log("Employee save was successful.");
				response.success(patron.get("first_name") + " " + patron.get("last_name"));
		});
	}

});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("request_redeem", function(request, response) {
	var storeId = request.params.store_id;
	var patronStoreId = request.params.patron_store_id;
	var rewardTitle = request.params.reward_title;
	var numPunches = request.params.num_punches;
	var customerName = request.params.customer_name;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var patronStore = new PatronStore();
	patronStore.id = patronStoreId;
	
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var redeemReward = new RedeemReward();
	redeemReward.set("customer_name", customerName);
	redeemReward.set("title", title);
	redeemReward.set("num_punches", numPunches);
	redeemReward.set("is_redeemed", false);
	redeemReward.set("PatronStore", patronStore);
	
	var Store = Parse.Object.extend("Store");
    var storeQuery = new Parse.Query(Store);
	storeQuery.include("RedeemRewards");
    storeQuery.equalTo("store_id", request.params.retailer_id);
	
	redeemReward.save().then(function(redeemReward) {
		console.log("RedeemReward save success.");
		return storeQuery.get(storeId);
		
	}, function(error) {
			console.log("RedeemReward save failed.");
			response.error("error");
			
	}).then(function(store) {
			console.log("Store fetch success.");
			store.relation("RedeemRewards").add(redeemReward);
			return store.save();
					
	}, function(error) {
			console.log("Store fetch failed.");
			response.error("error");	
			
	}).then(function(store) {
			console.log("Store save success.");
			executePush();
					
	}, function(error) {
			console.log("Store save failed.");
			response.error("error");			
	});
	
	function executePush() {
		var installationQuery = new Parse.Query(Parse.Installation);
		installationQuery.equalTo("store_id", storeId);
	    
		Parse.Push.send({
	        where: installationQuery,
	        data: {
	            alert: request.params.name + " wants to redeem a reward.",
				redeem_id: redeemReward.id,
	            badge: "Increment",
	            name: customerName,
	            num_punches: numPunches,
	            title: rewardTitle
	        }
	    }, {
	        success: function() {
				console.log("Push success.");
	            response.success("success");
	        },
	        error: function(error) {
				console.log("Push failed.");
	            response.error("error");
	        }
	    });
	}
                    
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("validate_redeem", function(request, response) {
	var redeemId = request.params.redeem_id;
	
	var patronId;
	var numPunches;
	var rewardTitle;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	redeemRewardQuery.include("PatronStore");
	
	redeemRewardQuery.get(redeemId).then(function(redeemReward) {
		console.log("RedeemReward fetch success.");
		var patronStore = redeemReward.get("PatronStore");
		numPunches = redeemReward.get("num_punches");
		
		if(patronStore == null) {
			console.log("PatronStore is null.");
			response.error("error");
			
		} else if(patronStore.get("punch_count") < numPunches) {
			console.log("PatronStore has insufficient punches.");
			response.error("error");
		} else{
			console.log("PatronStore has enough punches.");
			patronId = patronStore.get("Patron.id");
			patronStore.increment("punch_count", -1*numPunches);
			redeemReward.set("is_redeemed", true);
			
			var promises = [];
			promises.push( patronStore.save() );
			promises.push( redeemReward.save() );
			
			return Parse.Promise.when(promises);
		}
		
	}, function(error) {
			console.log("RedeemReward fetch failed.");
			response.error("error");
			
	}).then(function() {
			console.log("PatronStore and RedeemReward save success (in parallel).");
			executePush();
					
	}, function(error) {
			console.log("PatronStore and RedeemReward save fail (in parallel).");
			response.error("error");			
	});
	
	function executePush() {
		var installationQuery = new Parse.Query(Parse.Installation);
		installationQuery.equalTo("store_id", storeId);
		
		////below this is TODO.
	    
		Parse.Push.send({
	        where: installationQuery,
	        data: {
	            title: rewardTitle,
	            num_punches: numPunches,
				action: "com.repunch.intent.REDEEM"
	        }
	    }, {
	        success: function() {
				console.log("Push success.");
	            response.success("success");
	        },
	        error: function(error) {
				console.log("Push failed.");
	            response.error("error");
	        }
	    });
	}
});
 
////////////////////////////////////////////////////
// This is called by the server to check if the store has any new
// incoming data every X seconds.
// 
//  Input:
//      store objectId (to process rewards array redemption_count)
//      patronStore_count (count)
//      feedback_unread (count)
//      employees_pending (count)
//
//  Output: 
//      patronStore_count (if changed)
//      feedback_unread (if changed)
//      feedbacks (new objects) (if feedback_unread changed)
//      employees_pending (if changed)
//      employees (new objects) (if employees_pending changed)
//
////////////////////////////////////////////////////
Parse.Cloud.define("retailer_refresh", function(request, response) {
    var data;
    
    response.success(data);
});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("retailer_message", function(request, response) {
    // note that we could also query the PatronStores in the Store 
    // relation instead of querying the PatronStore class itself.
    var Store = Parse.Object.extend("Store");
    var Message = Parse.Object.extend("Message");
    var PatronStore = Parse.Object.extend("PatronStore");
    var Patron = Parse.Object.extend("Patron");
    var messageQuery = new Parse.Query(Message);
    var patronQuery = new Parse.Query(Patron);
    var patronStoreQuery = new Parse.Query(PatronStore);
    var installationQuery = new Parse.Query(Parse.Installation)
    var filter = request.params.filter;
    var message, patron_ids = new Array(); // placeholder

    function addToPatronsInbox(patronStores) {
        if (patronStores.length == 0 ){
            // match the installation with the username in the 
            if (filter === "one"){
                installationQuery.equalTo("patron_id", 
                                request.params.patron_id);
            } else {
                console.log(patron_ids);
                installationQuery.containedIn("patron_id", patron_ids);
            }
            // all tasks are done. Push now.
            proceedToPush();
            return;
        }
        
        var pt = patronStores.pop();
        var pat = pt.get("Patron");
        
        // keep track of atron ids for the installationQuery
        patron_ids.push(pat.id);
        
        console.log("NOW FETCHING PATRON FOR patronStore " + pt.id);
        var rel = pat.relation("ReceivedMessages"); 
        // message obtained from the beginning (bottom)
        rel.add(message);
        pat.save();
        // chain method call
        addToPatronsInbox(patronStores);
    }

    // class when all tasks are done
    function proceedToPush(){
        console.log("PROCEED TO PUSH");
        Parse.Push.send({
            where: installationQuery, 
            data: {
                action: "com.repunch.intent.MESSAGE",
                subject: request.params.subject,
                store_id: request.params.store_id,
                store_name: request.params.store_name,
                message_id: request.params.message_id,
            }, 
            }, {
                success: function() {
                    response.success("success");
                },
                error: function(error) {
                    response.error("error");
                }
        }); // end Parse.Push
    }// end proceedToPush
   
    function continueWithPush() {
        console.log("CONTINUE WITH PUSH");
        // get a subset of patrons
        if (filter === "all"){
            // nothing
        } else if (filter === "idle") {     
            patronStoreQuery.lessThan("updatedAt", 
                new Date(request.params.idle_date) );
        } else if (filter === "most_loyal") {
            patronStoreQuery.greaterThanOrEqualTo("all_time_punches", 
                request.params.min_punches);
        }  

        if (filter === "one"){
            // first get the patron
            patronQuery.get(request.params.patron_id).then(function(patron){
                patronStoreQuery.matchesQuery("Patron", patron);
                patronStoreQuery.first().then(function(pst){
                    var arr = new Array(pst);
                    addToPatronsInbox(arr);
                });
            });
        } else {
            patronStoreQuery.select("Patron");
            patronStoreQuery.include("Patron");
            
            // adding relation to all patron's ReceivedMessages
            patronStoreQuery.find().then(function(patronStores){
                addToPatronsInbox(patronStores);
            });
        }// end else

    } // end continueWithPush();

    console.log("STARTING SCRIPT");
    // script actually START HERE
    var storeQuery = new Parse.Query(Store);
    console.log("RUNNING STORE QUERY");
    // first get the store
    storeQuery.get(request.params.store_id, {
      success: function(store) {
        patronStoreQuery.equalTo("Store", store);
        // now get the message object
        console.log("RUNNING MESSAGE QUERY");
        messageQuery.get(request.params.message_id, {
          success: function(msg) {
            message = msg;
            continueWithPush();
          }, error: function(object, error){
                console.log(error);
            }
        }); // end messageQuery
      }, error: function(object, error){
            console.log(error);
        }
    });// end storeQuery
 
}); // end Parse.Cloud.define

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("send_feedback", function(request, response) {
	var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	var body = request.params.body;
	var subject = request.params.subject;
	var senderName = request.params.sender_name;
	
	var Store = Parse.Object.extend("Store");
	var Patron = Parse.Object.extend("Patron");
	var Message = Parse.Object.extend("Message");
	
	var message = new Message();
	message.set("message_type", "feedback");
	message.set("is_read", false);
	message.set("sender_name", senderName);
	message.set("store_id", storeId);
	message.set("subject", subject);
	message.set("body", body);
	
	message.save().then(function(message) {
		console.log("Message save was successful.");
		var storeQuery = new Parse.Query(Store);
		return storeQuery.get(storeId);
		
	}, function(error) {
		console.log("Message save failed.");
		response.error("error");
				
	}).then(function(store) {
		console.log("Store fetch was successful.");
		store.relation("ReceivedMessages").add(message);
		return store.save();
		
	}, function(error) {
		console.log("Store fetch failed.");
		response.error("error");
						
	}).then(function(store) {
		console.log("Store save was successful.");
		var patronQuery = new Parse.Query(Patron);
		return patronQuery.get(patronId);
		
	}, function(error) {
		console.log("Store save failed.");
		response.error("error");
					
	}).then(function(patron) {
		console.log("Patron fetch was successful.");
		patron.relation("SentMessages").add(message);
		return patron.save();	
		
	}, function(error) {
		console.log("Patron fetch failed.");
		response.error("error");
					
	}).then(function(patron) {
		console.log("Patron save was successful.");
		response.success("success");	
		
	}, function(error) {
		console.log("Patron save failed.");
		response.error("error");			
	})
});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("coupon_message", function(request, response) {
    response.success("Hello world!");
});
/*
function sendInfoMessage(audience, subject, body)
{
    Parse.Push.send({
        channels: [ "default" ],
        data: {
            alert: "Testing push notifications.",
            title: "Android system tray notification here"
        }
    }, {
        success: function() {
            // Push was successful
        },
        error: function(error) {
            // Handle error
        }
    });
}
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
function sendCouponMessage(audience, subject, body, couponTitle, couponExpireDate)
{
    Parse.Push.send({
        channels: [ "Giants", "Mets" ],
        data: {
            alert: "The Giants won against the Mets 2-3."
        }
    }, {
        success: function() {
            // Push was successful
        },
        error: function(error) {
            // Handle error
        }
    });
}
 
//function sendFeedbackReply(audience, )
*/
