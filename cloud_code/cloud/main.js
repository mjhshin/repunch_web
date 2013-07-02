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
	var user = new Parse.User();
	
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
				
	}).then(function(userResult) {
		console.log("User fetch success.");
		user = userResult;
		userResult.set("Patron", patron);
		userResult.set("account_type", "patron");
		
		if(email != null) {
			userResult.set("email", email);
		}
		  
		return userResult.save();
			
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
		
		if(error.code == Parse.Error.EMAIL_TAKEN) {
			console.log("User save failed because this email is already taken.");
			response.error(error.message);
			deleteAccount();
			
		} else {
			response.error("error");
		}	
	});
	
	function deleteAccount() {
		var promises = [];
		promises.push( user.destroy() );
		promises.push( patron.destroy() );
		
		Parse.Promise.when(promises).then(function(){
		    console.log("Patron and User delete success (in parallel).");
			
		}, function(error) {
		    console.log("Patron and User delete fail (in parallel).");
        });
	}
	
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
Parse.Cloud.define("add_patronstore", function(request, response) {
    var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var Patron = Parse.Object.extend("Patron");
	
	var patronStore = new PatronStore();
	var store = new Store();
	var patron = new Patron();
	
	var storeQuery = new Parse.Query(Store);
	var patronQuery = new Parse.Query(Patron);
	
	store.id = storeId;
	patron.id = patronId;
	
	patronStore.set("all_time_punches", 0);
	patronStore.set("punch_count", 0);
	patronStore.set("redeem_pending", false);
	patronStore.set("Store", store);
	patronStore.set("Patron", patron);
	
	patronStore.save().then(function(patronStore) {
		console.log("PatronStore save success.");
		return patronQuery.get(patronId);
		
	}, function(error) {
		console.log("PatronStore save failed.");
		response.error("error");
		return;
		
	}).then(function(patron) {
		console.log("Patron fetch success.");
		patron.relation("PatronStores").add(patronStore);
		return patron.save();
		
	}, function(error) {
		console.log("Patron fetch failed.");
		response.error("error");
		return;
		
	}).then(function(patron) {
		console.log("Patron save success.");
		return storeQuery.get(storeId);
		
	}, function(error) {
		console.log("Patron save failed.");
		response.error("error");
		return;
		
	}).then(function(store) {
		console.log("Store fetch success.");
		store.relation("PatronStores").add(patronStore);
		return store.save();
		
	}, function(error) {
		console.log("Store fetch failed.");
		response.error("error");
		return;
		
	}).then(function(patron) {
		console.log("Store save success.");
		response.success("success");
		return;
		
	}, function(error) {
		console.log("Store save failed.");
		response.error("error");
		return;
	}).then(function(){
	    // note that since memcached is used as the cache backend,
	    // the cache can be shared among all instances
        Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
	});
	
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("facebook_post", function(request, response) {
	var storeId = request.params.store_id;
	var patronStoreId = request.params.patron_store_id;
	var patronId = request.params.patron_id;
	var numPunches = request.params.num_punches;
	
    var Patron = Parse.Object.extend("Patron");
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var FacebookPost = Parse.Object.extend("FacebookPost");
	
	var patron = new Patron();
	patron.id = patronId;
	
	var facebookPost = new FacebookPost();
	facebookPost.set("Patron", patron);
	
	var patronStoreQuery = new Parse.Query(PatronStore);
	
	patronStoreQuery.get(patronStoreId).then(function(patronStore) {
		console.log("PatronStore fetch success.");
		patronStore.increment("all_time_punches", numPunches);
		patronStore.increment("punch_count", numPunches);
		return patronStore.save();
		
		var promises = [];
		promises.push( patronStore.save() );
		promises.push( facebookPost.save() );
	
		Parse.Promise.when(promises).then(function(facebookPost) {
		console.log("PatronStore and FacebookPost save success (in parallel).");
		var storeQuery = new Parse.Query(Store);
		return storeQuery.get(storeId);
		
	}, function(error) {
		console.log("PatronStore and FacebookPost save fail (in parallel).");
		response.error("error");
		return;
		
	}).then(function(store) {
		console.log("Store fetch success.");
		store.relation("FacebookPosts").add(facebookPost);
		return store.save();
		
	}, function(error) {
		console.log("Store fetch failed.");
		response.error("error");
		return;
		
	}).then(function(patron) {
		console.log("Store save success.");
		response.success("success");
		
	}, function(error) {
		console.log("Store save failed.");
		response.error("error");
		return;
		
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
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var Employee = Parse.Object.extend("Employee");
   
	var patronQuery = new Parse.Query(Patron);
	var patronStoreQuery = new Parse.Query(PatronStore);
	var storeQuery = new Parse.Query(Store);
	var androidInstallationQuery = new Parse.Query(Parse.Installation);
	var iosInstallationQuery = new Parse.Query(Parse.Installation);
   
	patronQuery.equalTo("punch_code", punchCode);
	storeQuery.equalTo("objectId", storeId);
	patronStoreQuery.matchesQuery("Patron", patronQuery);
	patronStoreQuery.matchesQuery("Store", storeQuery);
	patronStoreQuery.include("Patron");
	patronStoreQuery.include("Store");
	androidInstallationQuery.equalTo("punch_code", punchCode);
	androidInstallationQuery.equalTo('deviceType', 'android');
	iosInstallationQuery.equalTo("punch_code", punchCode);
	iosInstallationQuery.equalTo('deviceType', 'ios');
				   
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
		patronStore.set("redeem_pending", false);
								  
		patronQuery.first().then(function(patronResult) { //get Patron
			console.log("Patron fetched");
			patron = patronResult;
			patronStore.set("Patron", patronResult);
			return storeQuery.first();
			
		}, function(error) {
			console.log("Patron query failed.");
			response.error("error");	
			
		}).then(function(storeResult) { //get Store
			console.log("Store query success");
			store = storeResult;
			patronStore.set("Store", storeResult);
			return patronStore.save();
			
		}, function(error) {
			console.log("Store query failed.");
			response.error("error");
			
		}).then(function(patronStoreResult){
			console.log("PatronStore save success");
		    patronStore = patronStoreResult;
		    store.relation("PatronStores").add(patronStore);
			patron.relation("PatronStores").add(patronStore);
			
			var promises = [];
			promises.push( store.save() );
			promises.push( patron.save() );
		
			Parse.Promise.when(promises).then(function(){
			    console.log("Store and Patron save success (in parallel).");
				executePush(patronStore);
				saveDataForAnalytics(patronStore, true);
			
			}, function(error) {
			    console.log("Store and Patron save fail (in parallel).");
			    response.error("error");
	        });
			
		});
	}
	
	function updatePatronStore(patronStoreResult) {
		console.log("updating existing PatronStore");
		patronStoreResult.increment("punch_count", numPunches);
		patronStoreResult.increment("all_time_punches", numPunches);
		patron = patronStoreResult.get("Patron");
		patronStoreResult.save().then(function(patronStoreResult) {
			console.log("PatronStore save was successful.");
			executePush(patronStoreResult);
			saveDataForAnalytics(patronStoreResult, false);
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
		});
	}
	
	function executePush(patronStore) {
	    // TODO sync ios push reception with android?
		Parse.Push.send({
			where: androidInstallationQuery,
			data: {
				name: storeName,
				id: storeId,
				punches: numPunches,
				total_punches: patronStore.get("punch_count"),
				action: "com.repunch.intent.PUNCH"
			}
		}, {
			success: function() {
				console.log("Android push was successful");
			},
			error: function(error) {
				response.error("error");
			}
		});
		Parse.Push.send({
			where: iosInstallationQuery,
			data: {
				alert: storeName + " has punched you. BAM.",
				name: storeName,
				id: storeId,
				num_punches: numPunches,
				punch_type: "receive_punch"
			}
		}, {
			success: function() {
				console.log("iOS push was successful");
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
		}).then(function(){
	        // note that since memcached is used as the cache backend,
	        // the cache can be shared among all instances
            Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
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
	redeemReward.set("is_redeemed", false);
	redeemReward.set("PatronStore", patronStore);
	redeemReward.set("reward_id", rewardId);
	redeemReward.set("title", rewardTitle);
	redeemReward.set("num_punches", numPunches);
	redeemReward.set("PatronStore", patronStore);
	
	var Store = Parse.Object.extend("Store");
    var storeQuery = new Parse.Query(Store);
	var patronStoreQuery = new Parse.Query(PatronStore);
	
	patronStoreQuery.get(patronStoreId).then(function(patronStore) {
		console.log("PatronStore fetch success.");
		if(patronStore.get("redeem_pending") == true) {
			response.success("pending");
			return;
				
		} else {
			patronStore.set("redeem_pending", true);
			executeRedeemRequest(patronStore);
		}
					
	}, function(error) {
			console.log("PatronStore fetch failed.");
			response.error("error");
			return;		
	});
	
	function executeRedeemRequest(patronStore) {
		patronStore.save().then(function(patronStore) {
			console.log("PatronStore save success.");
			return redeemReward.save();

		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
			return;
			
		}).then(function(redeemReward) {
			console.log("RedeemReward save success.");
			return storeQuery.get(storeId);
		
		}, function(error) {
			console.log("RedeemReward save failed.");
			response.error("error");
			return;
			
		}).then(function(store) {
			console.log("Store fetch success.");
			store.relation("RedeemRewards").add(redeemReward);
			return store.save();
					
		}, function(error) {
			console.log("Store fetch failed.");
			response.error("error");
			return;	
			
		}).then(function(store) {
			console.log("Store save success.");
			executePush();
				
		}, function(error) {
			console.log("Store save failed.");
			response.error("error");
			return;			
		}).then(function(){
	        // note that since memcached is used as the cache backend,
	        // the cache can be shared among all instances
            Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
		});
	}
	
	function executePush() {
		var installationQuery = new Parse.Query(Parse.Installation);
		installationQuery.equalTo("store_id", storeId);
	    
		Parse.Push.send({
	        where: installationQuery,
	        data: {
	            alert: customerName + " wants to redeem a reward.",
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
				return;
	        },
	        error: function(error) {
				console.log("Push failed.");
	            response.error("error");
				return;
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
	var rewardId = request.params.reward_id;
	if (rewardId != null){ rewardId = parseInt(rewardId); }
	
	var patronId, numPunches, rewardTitle, storeName;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var Store = Parse.Object.extend("Store");
	var storeQuery = new Parse.Query(Store);
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	redeemRewardQuery.include(["PatronStore.Patron"]);
	
	storeQuery.get(storeId).then(function(store){
	    storeName = store.get("store_name");
	    if (rewardId != null){
	        var rewards = store.get("rewards");
		    // update the store's rewards redemption_count
		    for (var i=0; i<rewards.length; i++){
		        if (rewards[i].reward_id == rewardId){
		            rewards[i].redemption_count += 1;
		            break;
		        }
		    }
		    store.set("rewards", rewards);
		
		    return store.save();
		} 
	}).then(function(){
	    return redeemRewardQuery.get(redeemId);
		
	}).then(function(redeemReward) {
		var patronStore = redeemReward.get("PatronStore");
		console.log("RedeemReward fetch success.");
		numPunches = redeemReward.get("num_punches");
		rewardTitle = redeemReward.get("title");
		
		if(patronStore == null) {
			console.log("PatronStore is null.");
			response.error("error");
			return;
			
		} else if(patronStore.get("punch_count") < numPunches) {
			console.log("PatronStore has insufficient punches.");
			response.success("insufficient");
			return;
			
		} else{
			console.log("PatronStore has enough punches.");
			patronId = patronStore.get("Patron").id;
			patronStore.increment("punch_count", -1*numPunches);
			patronStore.set("redeem_pending", false);
			redeemReward.set("is_redeemed", true);
			
			var promises = [];
			promises.push( patronStore.save() );
			promises.push( redeemReward.save() );
			
			Parse.Promise.when(promises).then(function(){
			    console.log("PatronStore and RedeemReward save success (in parallel).");
			    executePush();
				
			}, function(error) {
			    console.log("PatronStore and RedeemReward save fail (in parallel).");
			    response.error("error");
	        });
		}
		
	}, function(error) {
			console.log("RedeemReward fetch failed.");
			response.error("error");
	}).then(function(){
	    // Since there may be multiple dashboards open and the mobile
	    // apps may validate redeems, dashboard needs to know about this
        Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
	});
	
	function executePush() {
		var installationQuery = new Parse.Query(Parse.Installation);
		installationQuery.equalTo("patron_id", patronId);
		Parse.Push.send({
	        where: installationQuery,
	        data: {
	            title: rewardTitle,
	            id: storeId, 
	            store: storeName, 
	            num_punches: numPunches,
				action: "com.repunch.intent.REDEEM"
	        }
	    }, {
	        success: function() {
				console.log("Push success.");
	            response.success("success");
				return;
	        },
	        error: function(error) {
				console.log("Push failed.");
	            response.error("error");
				return;
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
//      feedback_unread_ids (String array)
//      employees_pending_ids (String array)
//      redemption_ids (String array)
//
//  Output: 
//      rewards (empty if no redemption_count changed)
//      patronStore_count (if changed)
//      feedbacks (new objects) (if new stuff)
//      employees (new objects) (if new employees)
//      redemptions
//
////////////////////////////////////////////////////
Parse.Cloud.define("retailer_refresh", function(request, response) {
    var Store = Parse.Object.extend("Store");
    
    var store_id = request.params.store_id;
    var rewards_old = request.params.rewards;
    var patronStore_count = request.params.patronStore_count;
    var feedback_unread_ids = request.params.feedback_unread_ids;
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
    
        // feedbacks
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
    
        // employees
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
    var androidInstallationQuery = new Parse.Query(Parse.Installation);
    var iosInstallationQuery = new Parse.Query(Parse.Installation)
	
	var subject = request.params.subject;
	var messageId = request.params.message_id;
	var patronId = request.params.patron_id;
    var storeId = request.params.store_id;
	var storeName = request.params.store_name;
    var filter = request.params.filter; // one means a reply
    var message, patron_ids = new Array(); // placeholder

	androidInstallationQuery.equalTo('deviceType', 'android');
	iosInstallationQuery.equalTo('deviceType', 'ios');

    function addToPatronsInbox(patronStores) {
        if (patronStores.length == 0 ){
            // match the installation with the username in the 
            if (filter === "one"){
                androidInstallationQuery.equalTo("patron_id", patronId);
				iosInstallationQuery.equalTo("patron_id", patronId);
            } else {
                console.log(patron_ids);
                androidInstallationQuery.containedIn("patron_id", patron_ids);
				iosInstallationQuery.containedIn("patron_id", patron_ids);
            }
            Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
            // all tasks are done. Push now.
            proceedToPush();
            return
        }
        
        var pt = patronStores.pop();
        var pat = pt.get("Patron");
        
        // keep track of atron ids for the installationQuery
        patron_ids.push(pat.id);
        
        console.log("NOW FETCHING PATRON FOR patronStore ID " + pt.id);
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
        Parse.Push.send({
            where: androidInstallationQuery, 
            data: {
                action: "com.repunch.intent.MESSAGE",
                subject: subject,
                store_id: storeId,
                store_name: storeName,
                message_id: messageId,
            }, 
		}); // end Parse.Push

        Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
            	alert:request.params.store_name + " sent you a message: " + request.params.subject,
                subject: subject,
                store_id: storeId,
                store_name: storeName,
                message_id: messageId,
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
                parseInt(request.params.min_punches));
        }  

        if (filter === "one"){
            // first get the patron
            patronQuery.get(request.params.patron_id).then(function(patron){
                patronStoreQuery.equalTo("Patron", patron);
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
    storeQuery.get(storeId, {
      success: function(store) {
        patronStoreQuery.equalTo("Store", store);
        // now get the message object
        console.log("RUNNING MESSAGE QUERY");
        messageQuery.get(messageId, {
			success: function(msg) {
            	message = msg;
            	continueWithPush();
			}, error: function(object, error) {
                console.log(error);
			}
        }); // end messageQuery
	}, error: function(object, error) {
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
	}).then(function(){
	    Parse.Cloud.httpRequest({url: 'http://www.repunch.com/manage/comet/receive/' + storeId});
	});
});






