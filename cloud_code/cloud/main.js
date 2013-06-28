////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("register_patron", function(request, response) {
    var userObjectId = request.params.user_id;
	var username = request.params.username;
	var birthday = request.params.birthday;
	var gender = request.params.gender;
	var firstName = request.params.first_name;
	var lastName = request.params.last_name;
	var facebookId = request.params.facebook_id;
	var email = request.params.email;
	
	var Patron = Parse.Object.extend("Patron");
	var PunchCode = Parse.Object.extend("PunchCode");
	var patron = new Patron();
	
	var userQuery = new Parse.Query(Parse.User);
	var punchCodeQuery = new Parse.Query(PunchCode);
	punchCodeQuery.equalTo("is_taken", false);
	
	punchCodeQuery.first().then(function(punchCode) {
		console.log("PunchCode fetch success.");
        punchCode.set("is_taken", true);
        punchCode.set("username", username);
		return punchCode.save();
			
	}, function(error) {
		console.log("PunchCode fetch failed.");
		response.error("error");
		return;	
					
	}).then(function(punchCode) {
		console.log("PunchCode save success.");
		patron.set("first_name", firstName);
		patron.set("last_name", lastName);
		patron.set("gender", gender);
		patron.set("punch_code", punchCode.get("punch_code"));
		
		var year = birthday.substring(6, 10);
		var month = parseInt(birthday.substring(0, 2)) - 1;
		var day = birthday.substring(3, 5);
		var dateOfBirth = new Date(year, month, day);
		patron.set("date_of_birth", dateOfBirth);
		
		if(facebookId != null) {
			patron.set("facebook_id", facebookId);
		}
        
		return patron.save();
			
	}, function(error) {
		console.log("PunchCode save failed.");
		response.error("error");
		return;
				
	}).then(function(patronResult) {
		console.log("Patron save success.");
		patron = patronResult;
		return userQuery.get(userObjectId);
			
	}, function(error) {
		console.log("Patron save failed.");
		response.error("error");
		return;
				
	}).then(function(user) {
		console.log("User fetch success.");
		user.set("Patron", patron);
		user.set("account_type", "patron");
		
		if(email != null) {
			user.set("email", email);
		}
		  
		return user.save();
			
	}, function(error) {
		console.log("User fetch failed.");
		response.error("error");
		return;	
				
	}).then(function(user) {
		console.log("User save success. Registration complete!");
		response.success(patron.id);
		return;
			
	}, function(error) {
		console.log("User save failed.");
		response.error("error");
		return;			
	})
	
	
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("register_patron_facebook", function(request, response) {
    
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("register_employee", function(request, response) {
    
});

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
	var numPunches = parseInt(request.params.num_punches);
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
	// TEST ADD to store relation
	function addPatronStore() {
		console.log("customer's first punch at this store, adding new PatronStore.");
		var patronStore = new PatronStore(), store;
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
			store = storeResult;
			patronStore.set("Store", storeResult);
			return patronStore.save();
			
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
			
		}).then(function(patronStoreResult){ // save store
		    patronStore = patronStoreResult;
		    store.relation("PatronStores").add(patronStore);
		    return store.save();
		}).then(function(storeResult) {  // save patron
			console.log("saved PatronStore");
			patron.relation("PatronStores").add(patronStore);
			return patron.save();
			
		}, function(error) {
			console.log("Patron save failed.");
			response.error("error");
			
		}).then(function() {
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
		installationQuery.equalTo('deviceType', 'android');
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
		installationQuery.equalTo('deviceType', 'ios');
		Parse.Push.send({
			where: installationQuery,
			data: {
				name: storeName,
				id: storeId,
				num_punches: numPunches,
				punch_type: "receive_punch"
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
	var rewardTitle = request.params.title;
	var rewardId = parseInt(request.params.reward_id);
	var numPunches = parseInt(request.params.num_punches); //comes in as string!
	var customerName = request.params.name;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var patronStore = new PatronStore();
	patronStore.id = patronStoreId;
	
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var redeemReward = new RedeemReward();
	redeemReward.set("customer_name", customerName);
	redeemReward.set("num_punches", numPunches);
	redeemReward.set("is_redeemed", false);
	redeemReward.set("PatronStore", patronStore);
	redeemReward.set("reward_id", rewardId);
	redeemReward.set("title", rewardTitle);
	
	var Store = Parse.Object.extend("Store");
	var store;
    var storeQuery = new Parse.Query(Store);
	
	storeQuery.get(storeId).then(function(storeResult) {
		console.log("Store fetch success.");
		store = storeResult;
		
		return redeemReward.save();
		
	}, function(error) {
			console.log("Store fetch failed.");
			response.error("error");
			
	}).then(function(redeemReward) {
			console.log("RedeemReward save success.");
			store.relation("RedeemRewards").add(redeemReward);
			
			return store.save();
					
	}, function(error) {
			console.log("RedeemReward save failed.");
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
	            title: rewardTitle,
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
	var storeId = request.params.store_id;
	var rewardId = parseInt(request.params.reward_id);
	
	var patronId, numPunches, rewardTitle, storeName;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var Store = Parse.Object.extend("Store");
	var storeQuery = new Parse.Query(Store);
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	redeemRewardQuery.include(["PatronStore.Patron"]);
	
	storeQuery.get(storeId).then(function(store){
	    var rewards = store.get("rewards");
	    storeName = store.get("store_name");
		// update the store's rewards redemption_count
		for (var i=0; i<rewards.length; i++){
		    if (rewards[i].reward_id == rewardId){
		        rewards[i].redemption_count += 1;
		        rewardTitle = rewards[i].reward_name;
		        break;
		    }
		}
		store.set("rewards", rewards);
		
		return store.save();
	}).then(function(){
	    return redeemRewardQuery.get(redeemId);
	}).then(function(redeemReward) {
		var patronStore = redeemReward.get("PatronStore");
		console.log("RedeemReward fetch success.");
		numPunches = redeemReward.get("num_punches");
		
		if(patronStore == null) {
			console.log("PatronStore is null.");
			response.error("error");
			
		} else if(patronStore.get("punch_count") < numPunches) {
			console.log("PatronStore has insufficient punches.");
			response.error("error");
		} else{
			console.log("PatronStore has enough punches.");
			patronId = patronStore.get("Patron").id;
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
		installationQuery.equalTo("patron_id", patronId);
		Parse.Push.send({
	        where: installationQuery,
	        data: {
	            title: rewardTitle,
	            id: storeId, 
	            name: storeName, 
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
//      store objectId (for comparison with given values)
//      rewards (array object)
//      patronStore_count (count)
//      feedback_unread (count)
//      feedback_unread_ids (String array)
//      employees_pending (count)
//      employees_pending_ids (String array)
//      redemption_ids (String array)
//      // past_hour (UTC datetime for redemptions)
//
//  Output: 
//      rewards (empty if no redemption_count changed)
//      patronStore_count (if changed)
//      feedbacks (new objects) (if feedback_unread changed)
//      employees (new objects) (if employees_pending changed)
//      redemptions (latest redemptions the past hour limit of 20)
//
////////////////////////////////////////////////////
Parse.Cloud.define("retailer_refresh", function(request, response) {
    var Store = Parse.Object.extend("Store");
    
    var store_id = request.params.store_id;
    var rewards_old = request.params.rewards;
    var patronStore_count = request.params.patronStore_count;
    var feedback_unread = request.params.feedback_unread;
    var feedback_unread_ids = request.params.feedback_unread_ids;
    var employees_pending = request.params.employees_pending;
    var employees_pending_ids = request.params.employees_pending_ids;
    var redemption_ids = request.params.redemption_ids;
    // var past_hour = request.params.past_hour;
    var store, result = new Object();
    
    var storeQuery = new Parse.Query(Store);
    storeQuery.get(store_id).then(function(stor){
        console.log("Retrieved store");
        // rewards_old redemption_count
        store = stor;
        result.rewards = new Array();
        var rewards = store.get("rewards");
        function redemptionCount(reward){
            for (var i=0; i<rewards_old.length; i++){
                if(rewards_old[i].reward_name == reward.reward_name
                    && rewards_old[i].redemption_count !=
                        reward.redemption_count){
                    result.rewards.push({
                        "reward_name":reward.reward_name,
                        "redemption_count":reward.redemption_count});
                    break;
                }
            }
        }
        for (var i=0; i<rewards.length; i++){
            redemptionCount(rewards[i]);
        }
        
        // patronStore_count
        var psrq = store.relation("PatronStores").query();
        return psrq.count();
    }).then(function(newPatronStore_count){
        console.log("Retrieved PatronStore count");
        if (newPatronStore_count != patronStore_count){
            result.patronStore_count = newPatronStore_count;
        }
    
        // feedback_unread
        var rmrq = store.relation("ReceivedMessages").query();
        rmrq.equalTo("is_read", false);
        rmrq.equalTo("message_type", "feedback");
        rmrq.notContainedIn("objectId", feedback_unread_ids);
        return rmrq.find();
    }).then(function(newFeedbacks){
        console.log("Retrieved Feedbacks");
        if(newFeedbacks.length > 0){
            result.feedbacks = newFeedbacks;
        }
    
        // employees_pending
        var eprq = store.relation("Employees").query();
        eprq.equalTo("status", "Pending");
        eprq.notContainedIn("objectId", employees_pending_ids);
        return eprq.find();
    }).then(function(pendingEmployees){
        console.log("Retrieved PendingEmployees");
        if(pendingEmployees.length > 0){
            result.employees = pendingEmployees;
        }
        
        // redemptions
        var rrq = store.relation("RedeemRewards").query();
        // rrq.greaterThanOrEqualTo("createdAt", new Date(past_hour));
        rrq.equalTo("is_redeemed", false);
        rrq.descending("createdAt");
        // rrq.limit(40);
        // TODO remove this
        rrq.notContainedIn("objectId", redemption_ids);
        return rrq.find();
    }).then(function(redemptions){
        console.log("Retrieved Redemptions");
        // TODO check for changes- not just new ones
        // to remove the redeemed ones in the store's cache
        if (redemptions.length > 0){
            result.redemptions = redemptions;
        }
    
        response.success(result);
        return;
    });
    
});
 
////////////////////////////////////////////////////
//  Sends the store's message to a selected group of patrons
//  in the Store's PatronStore Relation. 
//  
//  This adds the message to each Patron's ReceivedMessages.
//  Replies to feedback does not add the reply itself to the
//  Patron's ReceivedMessages but rather the original message itself.
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
    var filter = request.params.filter; // one means a reply
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
        pat.save().then(function(){
            // chain method call
            addToPatronsInbox(patronStores);
        });
    }

    // call when all tasks are done
    function proceedToPush(){
        console.log("PROCEED TO PUSH");
        installationQuery.equalTo('deviceType', 'android');
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

        installationQuery.equalTo('deviceType', 'ios');
        Parse.Push.send({
            where: installationQuery, 
            data: {
                subject: request.params.subject,
                store_id: request.params.store_id,
                store_name: request.params.store_name,
                message_id: request.params.message_id,
                punch_type: "receive_message"
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
                patronStoreQuery.include("Patron");
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
	message.set("patron_id", patronId);
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
