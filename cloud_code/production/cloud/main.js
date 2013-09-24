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
        punchCode.set("username", email);
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
		
		if(email != null) {
			userResult.set("email", email);
			userResult.set("username", email);
		}
		  
		return userResult.save();
			
	}, function(error) {
		console.log("User fetch failed.");
		response.error("error");
		return;	
				
	}).then(function(user) {
		console.log("User save success. Registration complete!");
		response.success(patron);
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
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Patron and User delete success (in parallel).");
			
		}, function(error) {
		    console.log("Patron and User delete fail (in parallel).");
        });
	}
	
});

////////////////////////////////////////////////////
//
//  Handles employee registration. A USERNAME_TAKEN_AVAILABLE or
//  EMAIL_TAKEN_AVAILABLE error is returned if the Parse.User object 
//  associated with the given email/username does not yet have an Employee pointer.
//
//  WARNING! Email address in Parse.User is case sensitive!
//  This does not lower the email. Make sure to pass in email in all lower case.
//
////////////////////////////////////////////////////
Parse.Cloud.define("register_employee", function(request, response) {
	var retailerPin = request.params.retailer_pin;
    var username = request.params.username;
	var password = request.params.password;
	var firstName = request.params.first_name;
	var lastName = request.params.last_name;
	var email = request.params.email;
	
	var Employee = Parse.Object.extend("Employee");
	var Store = Parse.Object.extend("Store");
	var Settings = Parse.Object.extend("Settings");
	
	var employee, store;
	
	var settingsQuery = new Parse.Query(Settings);
	settingsQuery.include("Store");
	settingsQuery.equalTo("retailer_pin", retailerPin);
	
	settingsQuery.first().then(function(settings) {
		if(settings == null) {
			console.log("Settings fetch success, PIN invalid.");
			response.error("RETAILER_PIN_INVALID");
			
		} else {
			console.log("Settings fetch success, PIN valid.");
			executeSignUp(settings);
		}		
			
	}, function(error) {
		console.log("Settings fetch failed.");
		response.error("error");
		
	});
	
	function executeSignUp(settings) {
	    store = settings.get("Store");
	
		employee = new Employee();
		employee.set("first_name", firstName);
		employee.set("last_name", lastName);
		employee.set("lifetime_punches", 0);
		employee.set("status", "pending");
		employee.set("Store", store);
		
		employee.save().then(function(employee) {
			console.log("Employee save success.");

			var user = new Parse.User();
			user.set("username", username);
			user.set("password", password);
			user.set("email", email);
			user.set("Employee", employee);
			
			return user.signUp();
			
		}, function(error) {
			console.log("Employee save failed.");
			response.error("error");
			return;
				
		}).then(function(user) {
			console.log("User save success.");
			addEmployeeToStore();		
			
		}, function(error) {
			console.log("User save failed.");
		
			if(error.code == Parse.Error.USERNAME_TAKEN) {
				console.log("User save failed - username already taken.");
				associatedUserDetected("username");
				
			} else if(error.code == Parse.Error.EMAIL_TAKEN) {
			    console.log("User save failed - email already taken.");
				associatedUserDetected("email");
				
			} else if(error.code == Parse.Error.INVALID_EMAIL_ADDRESS) {
			    console.log("User save failed - email is invalid.");
			    response.error("EMAIL_INVALID");
			    deleteEmployee();
				
			} else {
				response.error("error");
			    deleteEmployee();
			}
			
		});
	}
	
	// email = username but differentiate anyways since 
	// this is still taking email and username as separate params
	function associatedUserDetected(which) {
	    var userQuery = new Parse.Query(Parse.User);
	    var error;
	    if(which == "email") {
	        userQuery.equalTo("email", email);
	        error = "EMAIL_TAKEN";
	    } else {
	        userQuery.equalTo("username", username);
	        error = "USERNAME_TAKEN";
	    }
	    
	    userQuery.first().then(function(user) {
	        if(user.get("Employee") == null) {
                response.error(error + "_AVAILABLE");
	        } else {
	            response.error(error);
	        }
			deleteEmployee();
			
	    });
	    
	}
	
	function addEmployeeToStore() {
		store.relation("Employees").add(employee);
		
		store.save().then(function(store) {
			console.log("Store save success.");
			response.success("success");
			
			Parse.Cloud.httpRequest({
                method: "POST",
                url: "https://www.repunch.com/manage/comet/receive/" + store.id,
                headers: { "Content-Type": "application/json"},
                body: { 
                    "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                    pendingEmployee: employee, 
                }
            });
			
		}, function(error) {
			console.log("Store save failed.");
			response.error("error");
				
		});
	}
	
	function deleteEmployee() {
		employee.destroy().then(function() {
			console.log("Employee delete success.");
			
		}, function(error) {
			console.log("Employee delete fail.");
		});
	}
    
});

////////////////////////////////////////////////////
//
//  Creates an employee and sets it to the given Parse.User.
//  EMPLOYEE_EXIST error if the given Parse.User already has an employee pointer.
//
////////////////////////////////////////////////////
Parse.Cloud.define("link_employee", function(request, response) {  
	var retailerPin = request.params.retailer_pin;
    var username = request.params.username;
	var firstName = request.params.first_name;
	var lastName = request.params.last_name;
	var email = request.params.email;
	
	var Employee = Parse.Object.extend("Employee");
	var Store = Parse.Object.extend("Store");
	var Settings = Parse.Object.extend("Settings");
	
	var employee, store;
	
	var userQuery = new Parse.Query(Parse.User);
	var settingsQuery = new Parse.Query(Settings);
	
	// yes username = email but check both anyways
	userQuery.equalTo("username", username);
	userQuery.equalTo("email", email);
	
	settingsQuery.include("Store");
	settingsQuery.equalTo("retailer_pin", retailerPin);
	
	
    // Note that the master key is not necessary to create a Parse.User.
    // However, it is necessary to modify an existing one.
    Parse.Cloud.useMasterKey(); 
	
	settingsQuery.first().then(function(settings) {
		if(settings == null) {
			console.log("Settings fetch success, PIN invalid.");
			response.error("RETAILER_PIN_INVALID");
			
		} else {
			console.log("Settings fetch success, PIN valid.");
			executeLink(settings);
		}		
			
	}, function(error) {
		console.log("Settings fetch failed.");
		response.error("error");
		
	});
	
	function executeLink(settings) {
		store = settings.get("Store");
		
		employee = new Employee();
		employee.set("first_name", firstName);
		employee.set("last_name", lastName);
		employee.set("lifetime_punches", 0);
		employee.set("status", "pending");
		employee.set("Store", store);
		
		employee.save().then(function(employee) {
			console.log("Employee save success.");
			return userQuery.first();
			
		}, function(error) {
			console.log("Employee save failed.");
			return Parse.Promise.error("error");
				
		}).then(function(user) {
		    if (user == null) {
			    return Parse.Promise.error("USER_NOT_FOUND");
			    
		    } else {
		        if (user.get("Employee") == null) {
		            user.set("Employee", employee);
		            return user.save();
		        } else {
			        return Parse.Promise.error("EMPLOYEE_EXIST");
		        }
		        
		    }
		
		}, function(error) {
			console.log("User query failed.");
			return Parse.Promise.error("error");
				
		}).then(function(user) {
			console.log("User save & employee link success.");
			addEmployeeToStore();
		    
		}, function(error) {
		    deleteEmployee();
		    response.error(error);
		});
		
	}
	
	function addEmployeeToStore() {
		store.relation("Employees").add(employee);
		
		store.save().then(function(store) {
			console.log("Store save success.");
			response.success("success");
			
			Parse.Cloud.httpRequest({
                method: "POST",
                url: "https://www.repunch.com/manage/comet/receive/" + store.id,
                headers: { "Content-Type": "application/json"},
                body: { 
                    "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                    pendingEmployee: employee, 
                }
            });
			
		}, function(error) {
			console.log("Store save failed.");
			response.error("error");
				
		});
	}
	
	function deleteEmployee() {
		employee.destroy().then(function() {
			console.log("Employee delete success.");
			
		}, function(error) {
			console.log("Employee delete fail.");
		});
	}
  
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
	patronStore.set("pending_reward", false);
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
		
	}).then(function(store) {
		console.log("Store save success.");
		// calling response.success here will prevent the following promises from executing!
		// response.success(patronStore);
	    return store.relation("PatronStores").query().count();
		
	}, function(error) {
		console.log("Store save failed.");
		response.error("error");
		return;
		
	}).then(function(patronStoreCount) {
        Parse.Cloud.httpRequest({
            method: "POST",
            url: "https://www.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: { 
                "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                patronStore_int: patronStoreCount,
            }
        });
        
        response.success(patronStore);
        
	});
	
});

////////////////////////////////////////////////////
//
// 
// 
////////////////////////////////////////////////////
Parse.Cloud.define("delete_patronstore", function(request, response) {
	var patronStoreId = request.params.patron_store_id;
    var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var Patron = Parse.Object.extend("Patron");
	
	var patronStoreQuery = new Parse.Query(PatronStore);
	var storeQuery = new Parse.Query(Store);
	var patronQuery = new Parse.Query(Patron);
	
	var patronStore, store, patron;
	
	var promises = [];
	promises.push( patronStoreQuery.get(patronStoreId) );
	promises.push( storeQuery.get(storeId) );
	promises.push( patronQuery.get(patronId) );
	
	Parse.Promise.when(promises).then(function(patronStoreResult, store, patron) {
		console.log("PatronStore/Store/Patron fetch success (in parallel).");
		patronStore = patronStoreResult;
		
		// this shouldn't be necessary since deleting the patronStore
		// will automatically remove it from all relations
		store.relation("PatronStores").remove(patronStore);
		patron.relation("PatronStores").remove(patronStore);
		
		var promises2 = [];
		promises2.push( store.save() );
		promises2.push( patron.save() );
		
		return Parse.Promise.when(promises2);

	}, function(error) {
		console.log("PatronStore/Store/Patron fetch fail (in parallel).");
		response.error("error");
		return;
		
	}).then(function() {
		console.log("Store/Patron save success (in parallel).");
		return patronStore.destroy();

	}, function(error) {
		console.log("Store/Patron save fail (in parallel).");
		response.error("error");
		return;
		
	}).then(function() {
		console.log("PatronStore delete success.");
		response.success("success");

	}, function(error) {
		console.log("PatronStore delete fail.");
		response.error("error");
		return;
	});
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("facebook_post", function(request, response)
{
	var patronStoreId = request.params.patron_store_id;
	var acceptPost = (request.params.accept == "true");
	
    var PatronStore = Parse.Object.extend("PatronStore");
	var patronStoreQuery = new Parse.Query(PatronStore);
	patronStoreQuery.include("Store");
	patronStoreQuery.include("Patron");
	
	patronStoreQuery.get(patronStoreId).then(function(patronStore)
	{
		console.log("PatronStore fetch success.");

		if(acceptPost)
		{
			var facebookPost = patronStore.get("FacebookPost");
			
			if(facebookPost != null)
			{
				var store = patronStore.get("Store");
				var freePunches = store.get("punches_facebook");
		
				store.relation("FacebookPosts").add( facebookPost );
		
				patronStore.increment("all_time_punches", freePunches);
				patronStore.increment("punch_count", freePunches);
				patronStore.set("FacebookPost", null);
		
				var promises = [];
				promises.push( store.save() );
				promises.push( patronStore.save() );
	
				Parse.Promise.when(promises).then(function() {
					console.log("Store and PatronStore save success (in parallel).");
					response.success("success");
					return;
		
				}, function(error) {
					console.log("Store and PatronStore save fail (in parallel).");
					response.error("error");
					return;
      	  		});
			}
			else
			{
				console.log("PatronStore has a null pointer to FacebookPost");
				response.error("error"); //TODO: once app handles this, we can change to success code.
			}
		}
		else
		{
			console.log("User declined to post to Facebook");
			patronStore.set("FacebookPost", null);
			patronStore.save().then(function() {
				console.log("PatronStore save success.");
				response.success("success");
				return;
		
			}, function(error) {
				console.log("PatronStore save fail.");
				response.error("error");
				return;
			});
		}
				
	}, function(error) {
		console.log("PatronStore fetch fail.");
		response.error("error");
		return;
	});
	
});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("punch", function(request, response)
{
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
				   
	patronStoreQuery.find({
		success: function(patronStoreResults) {
			if(patronStoreResults[0] == null) { //customer's first punch at this store, need new PatronStore.
				addPatronStore();				
			} else if(patronStoreResults.length > 1) {
				console.log("ERROR: more than one PatronStore found.");
				response.error("error");
			} else {
				updatePatronStore(patronStoreResults[0]);
			}
		},
		error: function(error) {
			console.log("PatronStore query failed.");
			response.error("error");
		}
	});
	
	function addPatronStore()
	{
		console.log("customer's first punch at this store, adding new PatronStore.");
		
		patronQuery.first().then(function(patronResult)
		{		
			if(patronResult == null)
			{
				console.log("Patron not found");
				response.error("PATRON_NOT_FOUND");
			}
			else
			{
				console.log("Patron fetched");
				
				var patronStore = new PatronStore();
				patronStore.set("punch_count", numPunches);
				patronStore.set("all_time_punches", numPunches);
				patronStore.set("pending_reward", false);
				patronStore.set("Patron", patronResult);
				
				storeQuery.first().then(function(storeResult) {
					console.log("Store query success");
					patronStore.set("Store", storeResult);
					return patronStore.save();
			
				}, function(error) {
					console.log("Store query failed.");
					response.error("error");
			
				}).then(function(patronStoreResult){
					console.log("PatronStore save success");
				    var store = patronStoreResult.get("Store");
				    var patron = patronStoreResult.get("Patron");
				    store.relation("PatronStores").add(patronStore);
					patron.relation("PatronStores").add(patronStore);
			
					var promises = [];
					promises.push( store.save() );
					promises.push( patron.save() );
		
					Parse.Promise.when(promises).then(function() {
					    console.log("Store and Patron save success (in parallel).");
						executePush(patronStore);
						saveDataForAnalytics(patronStoreResult, true);
			
					}, function(error) {
					    console.log("Store and Patron save fail (in parallel).");
					    response.error("error");
			        });
			
				});
			}
			
		}, function(error) {
			console.log("Patron query failed.");
			response.error("error");
		});
	}
	
	function updatePatronStore(patronStoreResult)
	{
		console.log("updating existing PatronStore");
		patronStoreResult.increment("punch_count", numPunches);
		patronStoreResult.increment("all_time_punches", numPunches);
		patronStoreResult.save().then(function(patronStoreResult)
		{
			console.log("PatronStore save was successful.");
			executePush(patronStoreResult);
			saveDataForAnalytics(patronStoreResult, false);
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
		});
	}
	
	function executePush(patronStore)
	{
		var punchString = (numPunches == 1) ? "punch" : "punches";
		var promises = [];
		promises.push( Parse.Push.send({
            where: androidInstallationQuery, 
			data: {
				name: storeName,
				id: storeId,
				punches: numPunches,
				total_punches: patronStore.get("punch_count"),
				action: "com.repunch.intent.PUNCH"
			}
        }) );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
			data: {
				type: "punch",
				alert: "Received " + numPunches + " " + punchString + " from " + storeName,
				store_id: storeId,
				patron_store_id: patronStore.id,
				punches: numPunches,
				total_punches: patronStore.get("punch_count"),
			}
            
        }) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	}
	
	function saveDataForAnalytics(patronStore, isNewPatronStore)
	{
		var Punch = Parse.Object.extend("Punch");
		var punch = new Punch();
	    var store = patronStore.get("Store");
	    var patron = patronStore.get("Patron");
	    var postBody = new Object();
		
		punch.set("Patron", patronStore.get("Patron"));
		punch.set("punches", numPunches);
		punch.save().then(function(punch) {
			console.log("Punch save was successful.");
			store.relation("Punches").add(punch);
			
			if(isNewPatronStore) {
				store.relation("PatronStores").add(patronStore);
			}
			
			return store.save();
			
		}, function(error) {
				console.log("Store save failed.");
				response.error("error");
				
		}).then(function(storeResult) {
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
				if(employee != null) {
					console.log("Employee fetched.");
					employee.relation("Punches").add(punch);
					employee.increment("lifetime_punches", numPunches);
					return employee.save();
				}
				
		}, function(error) {
				console.log("Employee save failed.");
				response.error("error");	
				
		}).then(function(employee) {
		        // IMPORTANT! Once response.success or error is called, the next promise will nto execute!
				// response.success(patron.get("first_name") + " " + patron.get("last_name"));
				
				// below are for server notification
		        if (employee != null) {
				    console.log("Employee save was successful.");
				    postBody.updatedEmployeePunch =  {
		                objectId: employee.id,
		                lifetime_punches: employee.get("lifetime_punches")
		            }  
				}
				
				if (isNewPatronStore) {
		            console.log("Retrieving new PatronStore count");
                    return store.relation("PatronStores").query().count();
                } else {
                    return -1;
                }
				
		}).then(function(patronStoreCount){
		    if (isNewPatronStore) {
		        console.log("Retrieved new PatronStore count");
		        postBody.patronStore_int = patronStoreCount;
		    }
		    
		    // Let the server know if any changes occured
		    if (isNewPatronStore || employeeId != null) {
		        console.log("Posting to server");
		        postBody.cometrkey = "f2cwxn35cxyoq8723c78wnvy";
		        Parse.Cloud.httpRequest({
                    method: "POST",
                    url: "https://www.repunch.com/manage/comet/receive/" + storeId,
                    headers: { "Content-Type": "application/json"},
                    body: postBody, 
                });
            }
            
            response.success(patron.get("first_name") + " " + patron.get("last_name"));
            
		}, function(error) {
		    console.log("There was an error retrieving the patronStore count.");		    
		});
	}

});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("request_redeem", function(request, response)
{
	var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	var patronStoreId = request.params.patron_store_id;
	var rewardTitle = request.params.title;
	var rewardId = parseInt(request.params.reward_id);
	var numPunches = parseInt(request.params.num_punches); //comes in as string!
	var customerName = request.params.name;
	var messageStatusId = request.params.message_status_id;
	var isOfferOrGift = (messageStatusId != null);
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var Store = Parse.Object.extend("Store");
	var Message = Parse.Object.extend("Message");
	
	var redeemReward = new RedeemReward();
	redeemReward.set("patron_id", patronId);
	redeemReward.set("customer_name", customerName);	
	redeemReward.set("is_redeemed", false);
	redeemReward.set("title", rewardTitle);
	
	var patronStore = new PatronStore();
	
	if(isOfferOrGift)
	{
		var MessageStatus = Parse.Object.extend("MessageStatus");
		var messageStatus = new MessageStatus();
		messageStatus.id = messageStatusId;
		redeemReward.set("num_punches", 0);
		redeemReward.set("MessageStatus", messageStatus);
		
		executeRedeemRequest();
	}
	else
	{
		patronStore.id = patronStoreId;
		redeemReward.set("PatronStore", patronStore);	
		redeemReward.set("num_punches", numPunches);
		redeemReward.set("reward_id", rewardId);
	
		var patronStoreQuery = new Parse.Query(PatronStore);
		patronStoreQuery.get(patronStoreId).then(function(patronStore)
		{
			console.log("PatronStore fetch success.");
		
			if(patronStore.get("pending_reward") == true)
			{
				console.log("PatronStore already has pending reward");
				response.success("pending");
				return;
			}
			else
			{
				patronStore.set("pending_reward", true);
				patronStore.save().then(function(patronStore)
				{
					console.log("PatronStore save success.");
					executeRedeemRequest();

				}, function(error) {
					console.log("PatronStore save failed.");
					response.error("error");
					return;
				});
			}				
		}, function(error) {
			console.log("PatronStore fetch failed.");
			response.error("error");
			return;		
		});
	}
	
	function executeRedeemRequest()
	{
		redeemReward.save().then(function(redeemReward)
		{
			console.log("RedeemReward save success.");
			var storeQuery = new Parse.Query(Store);
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
			if(isOfferOrGift) {
				updateMessageStatus();
			} else {
				executePush();
			}
				
		}, function(error) {
			console.log("Store save failed.");
			response.error("error");
			return;
					
		}).then(function() {
		    console.log("Posting to server");
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "https://www.repunch.com/manage/comet/receive/" + storeId,
                headers: {"Content-Type": "application/json"},
                body: { 
                    "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                    pendingRedemption: redeemReward, 
                },
                success: function(httpResponse) {
                    console.log("Post success");
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
            });
            
		});
	}
	
	function executePush() {
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
		iosInstallationQuery.equalTo("store_id", storeId);
	    iosInstallationQuery.equalTo("deviceType", "ios");
	    // TODO android push
	    
		Parse.Push.send({
	        where: iosInstallationQuery,
	        data: {
	            alert: customerName + " wants to redeem a reward",
				redeem_id: redeemReward.id,
	            badge: "Increment",
	            type: "request_redeem"
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
	
	function updateMessageStatus() {
		var MessageStatus = Parse.Object.extend("MessageStatus");
		var messageStatusQuery = new Parse.Query(MessageStatus);
		
		messageStatusQuery.get(messageStatusId).then(function(messageStatus)
		{
			console.log("MessageStatus query success.");
			messageStatus.set("redeem_available", "pending");
			return messageStatus.save();
				
		}, function(error) {
			console.log("MessageStatus query failed.");
			response.error("error");
			return;
			
		}).then(function(store) {
			console.log("MessageStatus save success.");
			executePush();
					
		}, function(error) {
			console.log("MessageStatus save failed.");
			response.error("error");
			return;	
			
		});
	}
                    
});


////////////////////////////////////////////////////
//
// Deletes the RedeemReward, sets the patron store's pending_reward to false IF IT IS NOT an offer!
// If RedeemReward does not have a reward_id, then it is an offer, which if it is
// the MessageStatus's redeem_available will be set 'no'.
//
////////////////////////////////////////////////////
Parse.Cloud.define("reject_redeem", function(request, response)
{
	var redeemId = request.params.redeem_id;
	var storeId = request.params.store_id;
	
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	var redeemReward, messageStatus;
	
	redeemRewardQuery.include("MessageStatus");
	redeemRewardQuery.include("PatronStore");
	redeemRewardQuery.get(redeemId).then(function(redeemRewardResult)
	{
	
	    if (redeemRewardResult.get("is_redeemed")) {
	        response.error("REDEEMREWARD_VALIDATED");
	    } else {
	        executeReject(redeemRewardResult);
        }
        
	}, function(error) {
		console.log("RedeemReward fetch failed.");
		response.error("REDEEMREWARD_NOT_FOUND"); // rejected/deleted before
		
	});
	
	function executeReject(redeemRewardResult) {
	    handleMessageStatus(redeemRewardResult).then(function() {
	        if (messageStatus == null) {
	            var patronStore = redeemReward.get("PatronStore");
			
	            if (patronStore != null) {
	                patronStore.set("pending_reward", false);
	                return patronStore.save();
	            }
	        }
	        
        }, function(error) {
            response.error(error);
	
        }).then(function() {
            return redeemReward.destroy();
            
        }).then(function() {
            Parse.Cloud.httpRequest({
                method: "POST",
                url: "https://www.repunch.com/manage/comet/receive/" + storeId,
                headers: { "Content-Type": "application/json"},
                body: {
                    "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                    deletedRedemption: redeemReward,
                },
            });
            
            response.success("success");
            
        });
        
    }
    
    function handleMessageStatus(redeemRewardResult) {
        var promise = new Parse.Promise();
	
        redeemReward = redeemRewardResult;
        messageStatus = redeemReward.get("MessageStatus");
	
        if (messageStatus != null) { // offer/gift
            messageStatus.set("redeem_available", 'no');
            messageStatus.save().then(function() {
                promise.resolve();
            }, function(error) {
                promise.resolve();
            });
        } else {
            promise.resolve();
        }
        
        return promise;  
    }
	
});


////////////////////////////////////////////////////
//
//  Called when removing an approved employee and denying a pending employee.
//
//  Params: 
//      employee_id: Employee object's objectId
//
//  Deletes the employee object and sends a push to the Installation with the given employee_id.
//  This will also delete the Parse.User associated with the Employee 
//  if it does not have a pointer to a Store and a Patron. Otherwise, 
//  the Employee pointer will just be set to null.
//
//  A push is made if the Employee status is "approved".
//
//  Note that this does not need to post to server because this is only called server side!
//  Meaning the notification is done within the server. 
//  Also removing the Employee's Parse.User from the Store's ACL is also done server side.
//
////////////////////////////////////////////////////
Parse.Cloud.define("delete_employee", function(request, response) 
{
    var employeeId = request.params.employee_id;
    var action = request.params.action;
    
    var EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND";
    
    var Employee = Parse.Object.extend("Employee");
    var employeeQuery = new Parse.Query(Employee);
    var userQuery = new Parse.Query(Parse.User)
    
	var androidInstallationQuery = new Parse.Query(Parse.Installation);
	var iosInstallationQuery = new Parse.Query(Parse.Installation);

	androidInstallationQuery.equalTo("employee_id", employeeId);
	androidInstallationQuery.equalTo("deviceType", "android");
	iosInstallationQuery.equalTo("employee_id", employeeId);
	iosInstallationQuery.equalTo("deviceType", "ios");
    
    employeeQuery.equalTo("objectId", employeeId); 
    userQuery.matchesQuery("Employee", employeeQuery);
    
    // Need to use the master key since we are modifying a Parse.User object.
    Parse.Cloud.useMasterKey(); 
    
    // Note that we must first retrive the user since deleting the employee
    // will make the userQuery return nothing.
    
    userQuery.first().then(function(user) 
    {
        // It will actually go here (not error) even if the employee does not exist!
        // Note the difference between Parse.Query.get and .first/.find
        // first() just returns find()[0], which may be null =)
        if (user == null) {
            console.log("Failed to retrieve User.");
            // Return a Parse error so that the following promises will not be called.
            return Parse.Promise.error(EMPLOYEE_NOT_FOUND);
        }
        
        if (user.get("Store") == null && user.get("Patron") == null) {
            console.log("User's Store and Patron pointers are null. Destroying User.");
            return user.destroy();
        } else {
            user.set("Employee", null);
            return user.save(); 
        }
        
    }).then(function(user) {
        console.log("User successfully destroyed/saved.");
        return employeeQuery.first();
        
    }).then(function(employee) {
        return employee.destroy();
    
    }).then(function(employee) {
        console.log("Employee successfully destroyed.");
        
        if (employee.get("status") == "approved") {
            var promises = [];
		    promises.push( Parse.Push.send({
	            where: androidInstallationQuery,
	            data: {
				    action: "com.repunch.intent.EMPLOYEE_DELETE"
	            }
	        }) );
		    promises.push( Parse.Push.send({
	            where: iosInstallationQuery,
	            data: {
				    type: "employee_delete",
	            }
	        }) );
		
		    return Parse.Promise.when(promises);
		}
        
    }).then(function() {
	    console.log("Android/iOS push successful");
		response.success("success");
		
	}, function(error) {
	    if (error == EMPLOYEE_NOT_FOUND) {
            console.log("Employee has already been deleted.");
        } else {
    	    console.log("Android/iOS push failed");
        }
        
		response.error(error);
		
	});
    
    
});


////////////////////////////////////////////////////
//
// 
//
////////////////////////////////////////////////////
Parse.Cloud.define("validate_redeem", function(request, response)
{
	var redeemId = request.params.redeem_id;
	var storeId = request.params.store_id;
	var rewardId = request.params.reward_id;
	
	var isOfferOrGift = (rewardId == null);
	
	var numPunches, rewardTitle, store, patron, patronId, patronStore,
	    updatedReward, messageStatus;
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var Store = Parse.Object.extend("Store");
	var MessageStatus = Parse.Object.extend("MessageStatus");
	
	var storeQuery = new Parse.Query(Store);
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	redeemRewardQuery.include(["PatronStore.Patron"]);
	redeemRewardQuery.include("MessageStatus");
	
	storeQuery.get(storeId).then(function(storeResult)
	{
		store = storeResult;
		
	    if (!isOfferOrGift) {
	        var reward_id = parseInt(rewardId);
	        
	        var rewards = store.get("rewards");
		    // update the store's rewards redemption_count
		    for (var i=0; i<rewards.length; i++) {
		        if (rewards[i].reward_id == reward_id) {
		            rewards[i].redemption_count += 1;
		            updatedReward = {
		                redemption_count: rewards[i].redemption_count,
		                reward_id: rewards[i].reward_id,
		            };
		            break;
		        }
		    }
		    store.set("rewards", rewards);	
		    return store.save();
		}
		
	}).then(function() {
	    return redeemRewardQuery.get(redeemId);
		
	}).then(function(redeemReward) {
		console.log("RedeemReward fetch success.");
		patronStore = redeemReward.get("PatronStore");
		numPunches = redeemReward.get("num_punches");
		rewardTitle = redeemReward.get("title");
		messageStatus = redeemReward.get("MessageStatus");
		patronId = redeemReward.get("patron_id");
		
		if(redeemReward.get("is_redeemed") == true) {
			console.log("RedeemReward has already been validated");
			response.success({ code:"validated", result: redeemReward });
			
		} else if(isOfferOrGift) {
			console.log("RedeemReward's reward_id is null, this is an offer/gift");
			redeemReward.set("is_redeemed", true);
			redeemReward.save().then(function() {
			    console.log("RedeemReward save success");
				postToServer(redeemReward);
			}, function(error) {
			    console.log("RedeemReward save fail");
			    response.error("error");
	        });
						
		} else if(patronStore.get("punch_count") < numPunches) {
			console.log("PatronStore has insufficient punches.");
			patronStore.set("pending_reward", false);
			patronStore.save().then(function()
			{
			    console.log("PatronStore save success");
			    
			    redeemReward.destroy().then(function() {
				    response.success({ code:"insufficient", result: redeemReward });
			    });
			}, function(error) {
			    console.log("PatronStore save fail");
			    response.error("error");
	        });
			
		} else {
			console.log("PatronStore has enough punches.");
			patron = patronStore.get("Patron");
			patronStore.increment("punch_count", -1*numPunches);
			patronStore.set("pending_reward", false);
			redeemReward.set("is_redeemed", true);
			
			var promises = [];
			promises.push( patronStore.save() );
			promises.push( redeemReward.save() );
			
			Parse.Promise.when(promises).then(function()
			{
			    console.log("PatronStore and RedeemReward save success (in parallel).");
			    
			    if(patron.get("facebook_id") != null && store.get("punches_facebook") > 0) {
					addFacebookPostToPatron(redeemReward);
				} else {
					postToServer(redeemReward);
				}
				
			}, function(error) {
			    console.log("PatronStore and RedeemReward save fail (in parallel).");
			    response.error("error");
	        });
		}
		
	}, function(error) {
			console.log("RedeemReward fetch failed.");
			response.error("REDEEMREWARD_NOT_FOUND"); // goes here if it has been deleted
			
	});
	
	function executePushReward(redeemReward)
	{
		var androidInstallationQuery = new Parse.Query(Parse.Installation);
		var iosInstallationQuery = new Parse.Query(Parse.Installation);

		androidInstallationQuery.equalTo("patron_id", patronId);
		androidInstallationQuery.equalTo("deviceType", "android");
		iosInstallationQuery.equalTo("patron_id", patronId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( Parse.Push.send({
	        where: androidInstallationQuery,
	        data: {
	            title: rewardTitle,
	            id: storeId, 
	            store: store.get("store_name"), 
	            punches: numPunches,
				total_punches: patronStore.get("punch_count"),
				action: "com.repunch.intent.REDEEM_REWARD"
	        }
	    }) );
		promises.push( Parse.Push.send({
	        where: iosInstallationQuery,
	        data: {
				type: "redeem",
	            alert: "Redeemed '" + rewardTitle + "'",
	            store_id: storeId,
				reward_title: rewardTitle,
				total_punches: patronStore.get("punch_count")
	        }
	    }) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success({ code:"success", result: redeemReward });
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	    
	}
	
	function executePushOfferGift(redeemReward)
	{
		var androidInstallationQuery = new Parse.Query(Parse.Installation);
		var iosInstallationQuery = new Parse.Query(Parse.Installation);

		androidInstallationQuery.equalTo("patron_id", patronId);
		androidInstallationQuery.equalTo("deviceType", "android");
		iosInstallationQuery.equalTo("patron_id", patronId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( Parse.Push.send({
	        where: androidInstallationQuery,
	        data: {
	            title: rewardTitle,
	            id: storeId, 
	            store: store.get("store_name"),
				message_status_id: messageStatus.id,
				action: "com.repunch.intent.REDEEM_OFFER_GIFT"
	        }
	    }) );
		promises.push( Parse.Push.send({
	        where: iosInstallationQuery,
	        data: {
				type: "redeem_offer_gift",
	            alert: "Redeemed '" + rewardTitle + "'",
	            message_status_id: messageStatus.id
	        }
	    }) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success({ code:"success", result: redeemReward });
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	}
	
	function addFacebookPostToPatron(redeemReward)
	{
		var freeFacebookPunches = store.get("punches_facebook");
	
		var FacebookPost = Parse.Object.extend("FacebookPost");
		var facebookPost = new FacebookPost();
		facebookPost.set("Patron", patron);
		facebookPost.set("reward", rewardTitle);
	
		facebookPost.save().then(function(facebookPost) {
			console.log("FacebookPost save success.");
			patronStore.set("FacebookPost", facebookPost);
			return patronStore.save();
			
		}, function(error) {
			console.log("FacebookPost save failed.");
			response.error("error");
			return;
	
		}).then(function() {
			console.log("PatronStore save success.");
			postToServer(redeemReward);
	
		}, function(error) {
			console.log("PatronStore save failed.");
			response.error("error");
			return;
		});
	}
	
	function updateMessageStatus(redeemReward)
	{
		messageStatus.set("redeem_available", "no");	
		messageStatus.save().then(function() {
			console.log("MessageStatus save success.");
			executePushOfferGift(redeemReward);
					
		}, function(error) {
			console.log("MessageStatus save failed.");
			response.error("error");
			return;	
			
		});
	}
	
	function postToServer(redeemReward)
	{
	    if(isOfferOrGift) {
			updateMessageStatus(redeemReward);
	    } else {
	        executePushReward(redeemReward);
	    }
	    
	    console.log("Posting to server");
	    var postBody = {
            "cometrkey": "f2cwxn35cxyoq8723c78wnvy",
	        approvedRedemption: redeemReward,
	    }
	    if(updatedReward != null) {
	        postBody.updatedReward = updatedReward;
	    }
	    Parse.Cloud.httpRequest({
            method: "POST",
            url: "https://www.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: postBody
        });
	}
	
});
 
////////////////////////////////////////////////////
//  Sends the store's message to a selected group of patrons
//  in the Store's PatronStore Relation. 
//  
//  This adds a MessageStatus, which is a wrapper around Message,
//  to each Patron's ReceivedMessages.
//  Replies to feedback does not add the reply itself to the
//  Patron's ReceivedMessages but rather the original message itself,
//  which is contained as a pointer in a newly created MessageStatus for each patron.
//
//  Note that this does not need to post to server because this is only called server side!
//  Meaning the notification is done within the server.
//
////////////////////////////////////////////////////
Parse.Cloud.define("retailer_message", function(request, response) {
   
    var Store = Parse.Object.extend("Store");
    var Message = Parse.Object.extend("Message");
    var MessageStatus = Parse.Object.extend("MessageStatus");
    var Patron = Parse.Object.extend("Patron");
    var messageQuery = new Parse.Query(Message);
    var patronQuery = new Parse.Query(Patron);
    var storeQuery = new Parse.Query(Store);
    var patronStoreQuery; 
	
	var subject = request.params.subject;
	var messageId = request.params.message_id;
	var patronId = request.params.patron_id;
    var storeId = request.params.store_id;
	var storeName = request.params.store_name;
    var filter = request.params.filter; 
    var message, receiver_count, redeem_available;
	var patron_ids = new Array(); 
	
	
    var androidInstallationQuery = new Parse.Query(Parse.Installation);
    var iosInstallationQuery = new Parse.Query(Parse.Installation);
	androidInstallationQuery.equalTo("deviceType", "android");
	iosInstallationQuery.equalTo("deviceType", "ios");

    storeQuery.get(storeId).then(function(storeResult) {
        patronStoreQuery = storeResult.relation("PatronStores").query();
        patronStoreQuery.include("Patron");
        patronStoreQuery.limit(999); 
        return messageQuery.get(messageId);
        
    }, function(error) {
		console.log("Store query failed.");
		response.error("error");
    }).then(function(messageResult) {
        message = messageResult;
        if (message.get("message_type") == "offer") {
            redeem_available = "yes";
        } else {
            redeem_available = "no";
        }
            
    }, function(error) {
        console.log("Message query failed");
        response.error("error");
                
    }).then(function() {
        if (filter === "one"){
            patronQuery.get(request.params.patron_id).then(function(patron) {
                patronStoreQuery.equalTo("Patron", patron);
                patronStoreQuery.first().then(function(patronStore) {
                    return addToPatronsInbox(new Array(patronStore));
                }).then(function() {
                    message.set("receiver_count", 1);
                    return message.save();
                }).then(function() {
                    console.log("Feedback message status created. Proceeding to push.");
                    proceedToPush();
                });
            });
            
        } else {
            if (filter === "idle") {
                patronStoreQuery.lessThan("updatedAt", 
                    new Date(request.params.idle_date) );
            } else if (filter === "most_loyal") {
                patronStoreQuery.descending("all_time_punches");
                patronStoreQuery.limit(request.params.num_patrons);
            }  
            
            patronStoreQuery.select("Patron");
            patronStoreQuery.find().then(function(patronStores) {
                receiver_count = patronStores.length;
                return addToPatronsInbox(patronStores);
            }).then(function() {
                message.set("receiver_count", receiver_count);
                return message.save();
            }).then(function() {
                console.log("All message status created. Proceeding to push.");
                proceedToPush();
            });
            
        }
        
    });
    
    function createMessageStatus(patron) { 
        var promise = new Parse.Promise();
        var receivedMessages = patron.relation("ReceivedMessages"); 
	    var messageStatus = new MessageStatus();
        messageStatus.set("Message", message);
        messageStatus.set("is_read", false);
        messageStatus.set("redeem_available", redeem_available);
        messageStatus.save().then(function(messageStatusResult) {
            receivedMessages.add(messageStatusResult);
            patron.save().then(function() {
                promise.resolve();
            });
        }, function(error) {
            // promise should still resolve
            promise.resolve();
        });
        
        return promise;
    }
    
    function addToPatronsInbox(patronStores) {
        var promises = [];
        // for some reason _.each says patronStores is undefined
        // also do not use for var i in array method- good ol' var i=0 is best
        for (var i=0; i < patronStores.length; i++) {
            var patron = patronStores[i].get("Patron");
            // there should not be any null patrons
            // null patrons will cause receiver_count to not match len of patron_ids
            if(patron == null) {
                console.log("PatronStore with id: " + patronStores[i].id + " has a null patron");
            } else {
                patron_ids.push(patron.id);
                console.log("Processing patronStore with id: " + patronStores[i].id);
                promises.push(createMessageStatus(patron));
            }
        }
        
        return Parse.Promise.when(promises);
    }
    
    function proceedToPush() { 
        if (filter === "one"){
            androidInstallationQuery.equalTo("patron_id", patronId);
			iosInstallationQuery.equalTo("patron_id", patronId);
        } else {
            androidInstallationQuery.containedIn("patron_id", patron_ids);
			iosInstallationQuery.containedIn("patron_id", patron_ids);
        }
		
		var promises = [];
		promises.push( Parse.Push.send({
            where: androidInstallationQuery, 
            data: {
                action: "com.repunch.intent.MESSAGE",
                subject: subject,
                store_id: storeId,
                store_name: storeName,
                message_id: messageId
            }
		}) );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
            	alert: storeName + " sent you a message",
                store_id: storeId,
                message_id: messageId,
                type: "message",
				badge: "Increment"
            }
		}) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success({
			    "result":"success",
			    "receiver_count": receiver_count,
			});
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	}
 
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
				
	}).then(function() {
	    Parse.Cloud.httpRequest({
            method: "POST",
            url: "https://www.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: {
                "cometrkey": "f2cwxn35cxyoq8723c78wnvy", 
                newFeedback: message,
            }
        });
            
	});
});

////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("send_gift", function(request, response) {
	var storeId = request.params.store_id;
	var patronId = request.params.patron_id;
	var patronStoreId = request.params.patron_store_id;
	var senderName = request.params.sender_name;
	var subject = request.params.subject;
	var body = request.params.body;
	var giftRecepientId = request.params.recepient_id;
	var giftTitle = request.params.gift_title;
	var giftDescription = request.params.gift_description;
	var giftPunches = request.params.gift_punches;
	
	var Store = Parse.Object.extend("Store");
	var Patron = Parse.Object.extend("Patron");
	var PatronStore = Parse.Object.extend("PatronStore");
	var Message = Parse.Object.extend("Message");
	var MessageStatus = Parse.Object.extend("MessageStatus");
	
	var patronQuery = new Parse.Query(Patron);
	
	var message = new Message();
	message.set("message_type", "gift");
	message.set("sender_name", senderName);
	message.set("store_id", storeId);
	message.set("patron_id", patronId);
	message.set("subject", subject);
	message.set("body", body);	
	message.set("gift_title", giftTitle);
	message.set("gift_description", giftDescription);
	
	var messageStatus = new MessageStatus();
	messageStatus.set("is_read", false);
	messageStatus.set("redeem_available", "yes");
	
	message.save().then(function(message) {
		console.log("Message save was successful.");
		messageStatus.set("Message", message);
		return messageStatus.save();
		
	}, function(error) {
		console.log("Message save failed.");
		response.error("error");
		
	}).then(function(messageStatus) {
		console.log("MessageStatus save success.");
		return patronQuery.get(giftRecepientId);
		
	}, function(error) {
		console.log("MessageStatus save failed.");
		response.error("error");
				
	}).then(function(patronRecepient) {
		console.log("Patron (recepient) fetch was successful.");
		patronRecepient.relation("ReceivedMessages").add(messageStatus);
		return patronRecepient.save();
		
	}, function(error) {
		console.log("Patron (recepient) fetch failed.");
		response.error("error");
						
	}).then(function(store) {
		console.log("Patron (recepient) save was successful.");
		return patronQuery.get(patronId);
		
	}, function(error) {
		console.log("Patron (recepient) save failed.");
		response.error("error");
					
	}).then(function(patronSender) {
		console.log("Patron (sender) fetch was successful.");
		patronSender.relation("SentMessages").add(message);
		return patronSender.save();	
		
	}, function(error) {
		console.log("Patron (sender) fetch failed.");
		response.error("error");
					
	}).then(function(patronSender) {
		console.log("Patron (sender) save was successful.");
		var patronStoreQuery = new Parse.Query(PatronStore);
		return patronStoreQuery.get(patronStoreId);
		
	}, function(error) {
		console.log("Patron (sender) save failed.");
		response.error("error");
			
	}).then(function(patronStore) {
		console.log("PatronStore fetch was successful.");
		if(patronStore.get("punch_count") < giftPunches) {
			console.log("PatronStore has insufficient punches");
			response.success("insufficient");
		} else {
			patronStore.increment("punch_count", -1*giftPunches);
			return patronStore.save();
		}
		
	}, function(error) {
		console.log("PatronStore fetch was failed.");
		response.error("error");
			
	}).then(function(patronStore) {
		console.log("PatronStore save successful.");
		executePush();
		
	}, function(error) {
		console.log("PatronStore save failed.");
		response.error("error");
			
	});
	
	function executePush() {
		var androidInstallationQuery = new Parse.Query(Parse.Installation);
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
 
		androidInstallationQuery.equalTo("patron_id", giftRecepientId);
		androidInstallationQuery.equalTo("deviceType", "android");
		iosInstallationQuery.equalTo("patron_id", giftRecepientId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( Parse.Push.send({
            where: androidInstallationQuery, 
            data: {
                action: "com.repunch.intent.GIFT",
                subject: subject,
                store_id: storeId,
                sender: senderName,
                message_status_id: messageStatus.id
			}
        }) );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
                alert: senderName + " sent you a gift",
                message_status_id: messageStatus.id,
                type: "gift",
				badge: "Increment"
			}
        }) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success("success");
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	}
});


////////////////////////////////////////////////////
//  
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("reply_to_gift", function(request, response) {
	var messageId = request.params.message_id;
	var senderName = request.params.sender_name;
	var body = request.params.body;
	
	var Patron = Parse.Object.extend("Patron");
	var Message = Parse.Object.extend("Message");
	var MessageStatus = Parse.Object.extend("MessageStatus");
	
	var message = new Message();
	message.set("message_type", "gift");
	message.set("body", body);
	message.set("is_read", false);
	message.set("sender_name", senderName);
	
	var messageStatus = new MessageStatus();
	messageStatus.set("is_read", false);
	messageStatus.set("redeem_available", "no");
	
	var receiverPatronId, subject, storeId;
	
	message.save().then(function(message) {
		console.log("Reply Message save successful.");
		messageStatus.set("Message", message);
		
		var messageQuery = new Parse.Query(Message);
		return messageQuery.get(messageId);
		
	}, function(error) {
		console.log("Reply Message save failed.");
		response.error("error");
			
	}).then(function(originalMessage) {
		console.log("Original Message fetch successful.");
		receiverPatronId = originalMessage.get("patron_id");
		subject = originalMessage.get("subject");
		storeId = originalMessage.get("store_id");
		
		originalMessage.set("Reply", message);
		messageStatus.set("Message", originalMessage);
		
		var promises = [];
		promises.push( originalMessage.save() );
		promises.push( messageStatus.save() );
		
		Parse.Promise.when(promises).then(function(originalMessage, messageStatus) {
		    console.log("Original Message and MessageStatus save success (in parallel).");
			var patronQuery = new Parse.Query(Patron);
			return patronQuery.get(receiverPatronId);
			
		}, function(error) {
		    console.log("Original Message and MessageStatus save fail (in parallel).");
		    response.error("error");
        
		}).then(function(receiverPatron) {
			console.log("Recepient Patron query successful.");
			receiverPatron.relation("ReceivedMessages").add(messageStatus);
			return receiverPatron.save();
		
		}, function(error) {
			console.log("Recepient Patron query failed.");
			response.error("error");
			
		}).then(function() {
			console.log("Recepient Patron save successful.");
			executePush();
		
		}, function(error) {
			console.log("Recepient Patron save failed.");
			response.error("error");
			
		});
		
	}, function(error) {
		console.log("Original Message fetch failed.");
		response.error("error");
			
	});
	
	function executePush() {
		var androidInstallationQuery = new Parse.Query(Parse.Installation);
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
 
		androidInstallationQuery.equalTo("patron_id", receiverPatronId);
		androidInstallationQuery.equalTo("deviceType", "android");
		iosInstallationQuery.equalTo("patron_id", receiverPatronId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( Parse.Push.send({
            where: androidInstallationQuery, 
            data: {
                action: "com.repunch.intent.GIFT",
                subject: "RE: " + subject,
                store_id: storeId,
                sender: senderName,
                message_status_id: messageStatus.id
			}
        }) );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
                alert: senderName + " replied to your gift",
                message_status_id: messageStatus.id,
                type: "gift_reply",
				badge: "Increment"
			}
        }) );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success(message);
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
		});
	}
	
});
