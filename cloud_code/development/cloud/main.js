////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("register_patron", function(request, response) {
    //var userObjectId = request.params.user_id;
	var email = request.params.email;
	var birthday = request.params.birthday;
	var gender = request.params.gender;
	var firstName = request.params.first_name;
	var lastName = request.params.last_name;
	var facebookId = request.params.facebook_id;
	
	var Patron = Parse.Object.extend("Patron");
	var PunchCode = Parse.Object.extend("PunchCode");
	var patron, user, punchCode;
	
	var punchCodeQuery = new Parse.Query(PunchCode);
	punchCodeQuery.equalTo("is_taken", false);
	
	punchCodeQuery.first().then(function(punchCodeResult) {
		console.log("PunchCode fetch success.");
        punchCodeResult.set("is_taken", true);
        punchCodeResult.set("user_id", request.user.get("objectId"));	//for record keeping purposes. also we use ParseUser.objectId
        											//since facebook users may not have email available.
		return punchCodeResult.save();
			
	}, function(error) {
		console.log("PunchCode fetch failed.");
		return Parse.Promise.error(error);
					
	}).then(function(punchCodeResult) {
	    punchCode = punchCodeResult;
	    
		console.log("PunchCode save success.");
		patron = new Patron();
		patron.set("first_name", firstName);
		patron.set("last_name", lastName);
		patron.set("gender", gender);
		patron.set("punch_code", punchCode.get("punch_code"));
		
		if (birthday != null && birthday.length > 0)
		{
		    var year = birthday.substring(6, 10);
		    var month = parseInt(birthday.substring(0, 2)) - 1;
		    var day = birthday.substring(3, 5);
		    var dateOfBirth = new Date(year, month, day);
		    patron.set("date_of_birth", dateOfBirth);
		}
		
		if(facebookId != null) {
			patron.set("facebook_id", facebookId);
		}
        
		return patron.save();
			
	}, function(error) {
		console.log("PunchCode save failed.");
		return Parse.Promise.error(error);
				
	}).then(function(patronResult) {
		console.log("Patron save success.");
		patron = patronResult;
		request.user.set("Patron", patron);
		
		if(email != null && facebookId == null) {
			request.user.set("email", email);
			request.user.set("username", email);
		}
		  
		return request.user.save();
			
	}, function(error) {
		console.log("Patron save failed.");
		return Parse.Promise.error(error);
				
	}).then(function(user) {
		console.log("User save success. Registration complete!");
		response.success(patron);
			
	}, function(error) {
		console.log("User save failed.");
		
		if(error.code == Parse.Error.EMAIL_TAKEN || error.code == Parse.Error.USERNAME_TAKEN) {
			console.log("User save failed because this username/email is already taken.");

		} else {
			console.log(error.message);
		}

		// we undo everything that might have been done
		var promises = [];
		
		// punch code will be null if we failed to fetch it
		if (punchCode != null) {
            punchCode.set("is_taken", false);
            punchCode.set("user_id", null);
		    promises.push( punchCode.save() );
		}
		
		// patron will be null if punch code save failed
		if (patron != null) {
		    promises.push( patron.destroy() ); // TODO: if this fails?
		}
		
		//destroy user object
		promises.push( request.user.destroy() );
		
		Parse.Promise.when(promises).then(function() {
		    console.log("Error correction success.");
            response.error("error");
			
		}, function(error) {
		    console.log("Error correction failed");
            response.error("error");
		    
        });
		
		
	});

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
	
	// optional parameters
	// punch_redeem, admin
	var access_level = request.params.access_level;
	
	// status or approved
	var status = request.params.status;
	if(status == null) {
	    status = "pending";
	}
	
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
		employee.set("status", status);
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
			addEmployeeToStore(user);		
			
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
	
	function addEmployeeToStore(employeeUser) {
		store.relation("Employees").add(employee);
		
		// set the acl if given
		var acl = store.getACL();
		if(access_level == "admin") {
		    acl.setReadAccess(employeeUser, true);
		    acl.setWriteAccess(employeeUser, true);
		} else if(access_level == "punch_redeem") {
		    acl.setReadAccess(employeeUser, true);
		} 
		store.setACL(acl);
		
		store.save().then(function(store) {
			console.log("Store save success.");
			response.success(employee);
			
			var postBody = { "cometrkey": "384ncocoacxpvgrwecwy" };
			if(status == "pending") {
                postBody.pendingEmployee = employee;
			} else {
                postBody.newEmployee = employee;
			}
			
			Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/manage/comet/receive/" + store.id,
                headers: { "Content-Type": "application/json"},
                body: postBody
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
//  EMPLOYEE_EXIST error if the given Parse.User already has an employee pointer
//
////////////////////////////////////////////////////
Parse.Cloud.define("link_employee", function(request, response) {  
	var retailerPin = request.params.retailer_pin;
    var username = request.params.username;
	var firstName = request.params.first_name;
	var lastName = request.params.last_name;
	var email = request.params.email;
	
	// optional parameters
	// punch_redeem, admin
	var access_level = request.params.access_level;
	
	// status or approved
	var status = request.params.status;
	if(status == null) {
	    status = "pending";
	}
	
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
		employee.set("status", status);
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
			addEmployeeToStore(user);
		    
		}, function(error) {
		    deleteEmployee();
		    response.error(error);
		});
		
	}
	
	function addEmployeeToStore(employeeUser) {
		store.relation("Employees").add(employee);
		
		// set the acl if given
		var acl = store.getACL();
		if(access_level == "admin") {
		    acl.setReadAccess(employeeUser, true);
		    acl.setWriteAccess(employeeUser, true);
		} else if(access_level == "punch_redeem") {
		    acl.setReadAccess(employeeUser, true);
		} 
		store.setACL(acl);
		
		store.save().then(function(store) {
			console.log("Store save success.");
			response.success(employee);
			
			var postBody = { "cometrkey": "384ncocoacxpvgrwecwy" };
			if(status == "pending") {
                postBody.pendingEmployee = employee;
			} else {
                postBody.newEmployee = employee;
			}
			
			Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/manage/comet/receive/" + store.id,
                headers: { "Content-Type": "application/json"},
                body: postBody
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

    var EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND";
    
    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
    var Employee = Parse.Object.extend("Employee");
    var employeeQuery = new Parse.Query(Employee);
    var userQuery = new Parse.Query(Parse.User);
    
	var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	var iosInstallationQuery = new Parse.Query(Parse.Installation);

	iosInstallationQuery.equalTo("employee_id", employeeId);
	iosInstallationQuery.equalTo("deviceType", "ios");
	androidInstallationQuery.equalTo("employee_id", employeeId);
    androidInstallationQuery.select("registration_id", "support");
    
    employeeQuery.equalTo("objectId", employeeId); 
    userQuery.matchesQuery("Employee", employeeQuery);
    
    // Need to use the master key since we are modifying a Parse.User object.
    Parse.Cloud.useMasterKey(); 
    
    function gcmPost() {
	    var promise = new Parse.Promise();
    
        androidInstallationQuery.find().then(function(installations) {
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for (var i=0; i<installations.length; i++) {
                repunchReceivers.push({
                    registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
                    employee_id: employeeId,
                });
            }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: {
                    gcmrkey: "p9wn84m8450yot4ureh",
                    repunch_receivers: repunchReceivers, 
			        action: "com.repunch.retailer.INTENT_EMPLOYEE_DELETED",
                }, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
    
        return promise;
    }
    
    // Note that we must first retrieve the user since deleting the employee
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
		    promises.push( gcmPost() );
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
Parse.Cloud.define("add_patronstore", function(request, response) {
    var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	
	var Store = Parse.Object.extend("Store");
	var Patron = Parse.Object.extend("Patron");
	var PatronStore = Parse.Object.extend("PatronStore");
	
	var patron = new Patron();
	var store = new Store();
	
	patron.id = patronId;
	store.id = storeId;
	
	var storeQuery = new Parse.Query(Store);
	var patronStoreQuery = new Parse.Query(PatronStore);
	
	patronStoreQuery.equalTo("Patron", patron);
	patronStoreQuery.equalTo("Store", store);
	
	// first check if the PatronStore already exists
    patronStoreQuery.first().then(function(patronStore) {
        if(patronStore == null) {
            console.log("No existing PatronStore found.");
            fetchPatronAndStore().then(function(patron, store) {
			    addPatronStore(patron, store);
			},
			function(error) {
			    console.log("Failed to fetch Patron and Store.");
			    console.log(error);
			    response.error("error");
			});
		}
		else {
            console.log("Existing PatronStore found.");
            fetchPatronAndStore().then(function(patron, store) {
			    linkExistingPatronStore(patron, store, patronStore).then(function() {
			    	console.log("Successfully added relation from PatronStore to Patron and Store.");
					response.success(patronStore);
			    },
			    function(error) {
			    	console.log("Failed to add relation from PatronStore to Patron and Store.");
			    	console.log(error);
			    	response.error("error");
			    });
			},
			function(error) {
			    console.log("Failed to fetch Patron and Store.");
			    console.log(error);
			    response.error("error");
			});
		}
    });
    
    function addPatronStore(patron, store) {
        console.log("Creating new PatronStore.");
    
        var patronStore = new PatronStore();
	    patronStore.set("all_time_punches", 0);
	    patronStore.set("punch_count", 0);
	    patronStore.set("pending_reward", false);
	    patronStore.set("Store", store);
	    patronStore.set("Patron", patron);

	    patronStore.save().then(function(patronStore) {
			patron.relation("PatronStores").add(patronStore);
			store.relation("PatronStores").add(patronStore);
			
            var promises = [];
            promises.push(patron.save());
            promises.push(store.save());

            return Parse.Promise.when(promises);	
            		
	    }).then(function(patron, store) {
	        console.log("Patron and Store save success.");
	        return store.relation("PatronStores").query().count();
	        
	    },
	    function(error) {
	        console.log("Patron and Store save failed.");
	        console.log(error);
	        
	    }).then(function(patronStoreCount) {
	        console.log("PatronStore count query success. Posting to dashboard.");
	        
	    	Parse.Cloud.httpRequest({
            	method: "POST",
            	url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
            	headers: { "Content-Type": "application/json"},
            	body: { 
                	"cometrkey": "384ncocoacxpvgrwecwy", 
                	patronStore_int: patronStoreCount,
            	}
        	});
        
        	response.success(patronStore);

	    },
	    function(error) {
	        console.log("PatronStore count query failed.");
	        console.log(error);
	        // still success here because we accomplished what we wanted to do
	        // even if we didn't manage to post the new PatronStore count to the dashboard.
        	response.success(patronStore);
	    
	    });
	    
    }
    
    function fetchPatronAndStore() {
        console.log("Fetching Patron and Store in parallel.");
        
        var promises = [];
        promises.push( patron.fetch() );
        promises.push( store.fetch() );

        return Parse.Promise.when(promises);	
    }

    function linkExistingPatronStore(patron, store, patronStore) {
        console.log("Adding relation from existing PatronStore to Patron and Store in parallel.");

        patron.relation("PatronStores").add(patronStore);
        store.relation("PatronStores").add(patronStore);
        
        var promises = [];
        promises.push( patron.save() );
        promises.push( store.save() );

        return Parse.Promise.when(promises);	
    }

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
	
	var patronStore;
	
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
		return Parse.Promise.error(error);
		
	}).then(function() {
		console.log("Store/Patron save success (in parallel).");
		response.success("success");

	}, function(error) {
		console.log("Store/Patron save fail (in parallel).");
		console.log(error);
		response.error("error");
		
	});
});

///////////////////////////////////////////////////////////////////
//
// 						POST_TO_FACEBOOK
//
// Will replace soon-to-be-deprecated FACEBOOK_POST function
// Performs actual posting (Facebook API call) and resolves
// its effects in Repunch
//
///////////////////////////////////////////////////////////////////
Parse.Cloud.define("post_to_facebook", function(request, response)
{
	// inputs - request.user containing Parse.User included by default
	var acceptPost = (request.params.accept == "true");
	var patronStoreId = request.params.patron_store_id;
	var rewardTitle = request.params.reward_title;
	var freePunches = request.params.free_punches;

	var PatronStore = Parse.Object.extend("PatronStore");
	var patronStoreQuery = new Parse.Query(PatronStore);

	patronStoreQuery.include("Store");
	
	patronStoreQuery.get(patronStoreId).then(function(patronStore)
	{
		console.log("PatronStore fetch success.");

		if(acceptPost)
		{
			if(patronStore.get("FacebookPost") == null)
			{
				console.error("FacebookPost pointer is null");
				response.error("NULL_FACEBOOK_POST");
			}
			else
			{
				executeFacebookPost(patronStore);
			}
		}
		else
		{
			console.log("User declined to post to Facebook");
			patronStore.set("FacebookPost", null);
			patronStore.save().then(function()
			{
				console.log("PatronStore save success");
				response.success("");
		
			}, function(error) {
				console.error("PatronStore save fail " + error.message);
				response.error("");
			});
		}
				
	}, function(error) {
		console.error("PatronStore query fail " + error.message);
		response.error("");
	});

	function executeFacebookPost(patronStore)
	{
		if ( Parse.FacebookUtils.isLinked(request.user) )
		{
			var store = patronStore.get("Store");

			Parse.Cloud.httpRequest({
				method: 'POST',

				//TODO: Move to Open Graph
				url:'https://graph.facebook.com/me/feed?'
						+ 'access_token=' + request.user.get('authData').facebook.access_token
						+ '&name=' + encodeURIComponent( 'Redeemed a reward using Repunch!' )
						+ '&caption=' + encodeURIComponent( 'At ' + store.get('store_name') )
						+ '&description=' + encodeURIComponent( rewardTitle )
						+ '&link=https://www.repunch.com/'
						+ '&picture=' + encodeURIComponent( store.get('thumbnail_image').url() ),

				success: function(httpResponse) {
		    		console.log(httpResponse.text);
		    		resolvePatronStore(patronStore);
	 			},
	  			error: function(httpResponse) {
	    			console.error('POST request failed with response code ' + httpResponse.text);
	    			response.error(httpResponse.status);
	  			}
	  		});
		}
		else
		{
			console.log("User not linked to a Facebook account");
			response.error("NOT_FACEBOOK_USER");
		}
	}

	function resolvePatronStore(patronStore)
	{
		var store = patronStore.get("Store");
		var facebookPost = patronStore.get("FacebookPost");
		
		store.relation("FacebookPosts").add( facebookPost );
		
		patronStore.increment("all_time_punches", freePunches);
		patronStore.increment("punch_count", freePunches);
		patronStore.set("FacebookPost", null);

		var promises = [];
		promises.push( store.save() );
		promises.push( patronStore.save() );

		Parse.Promise.when(promises).then(function()
		{
			console.log("Store and PatronStore save success (in parallel)");
			response.success("");

		}, function(error) {
			console.error("Store and PatronStore save fail (in parallel) " + error.message);
			response.error("");
	  	});
	}

});

///////////////////////////////////////////////////////////////////
//
// 						FACEBOOK_POST
//
// Resolves effect of posting to Facebook.
// DOES NOT perform the actual post (i.e. call Facebook API)
// Soon to be DEPRECATED
//
///////////////////////////////////////////////////////////////////
Parse.Cloud.define("facebook_post", function(request, response)
{
	var patronStoreId = request.params.patron_store_id;
	var acceptPost = (request.params.accept == "true");
	
    var PatronStore = Parse.Object.extend("PatronStore");
	var patronStoreQuery = new Parse.Query(PatronStore);
	patronStoreQuery.include("Store");
	
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
	var storeLocationId = request.params.store_location_id;
   
	var Patron = Parse.Object.extend("Patron");
	var PatronStore = Parse.Object.extend("PatronStore");
	var Store = Parse.Object.extend("Store");
	var Employee = Parse.Object.extend("Employee");
	var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
   
	var patronQuery = new Parse.Query(Patron);
	var patronStoreQuery = new Parse.Query(PatronStore);
	var storeQuery = new Parse.Query(Store);
	var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	var iosInstallationQuery = new Parse.Query(Parse.Installation);
	
	// subtract 1 compound query to patronStoreQuery.
	var store = new Store();
	store.id = storeId;
   
	patronQuery.equalTo("punch_code", punchCode);
	storeQuery.equalTo("objectId", storeId);
	
	patronStoreQuery.matchesQuery("Patron", patronQuery);
	patronStoreQuery.equalTo("Store", store);
	patronStoreQuery.include("Patron");
	patronStoreQuery.include("Store");
	
	androidInstallationQuery.equalTo("punch_code", punchCode);
	androidInstallationQuery.select("registration_id", "patron_id", "support");
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
	
	function gcmPost(patronStore){
	    var promise = new Parse.Promise();
	    
	    androidInstallationQuery.find().then(function(installations) {
	        console.log("Found "+installations.length+" installations for punch_code "+punchCode);
	    
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            console.log("Pushing installation "+installations[i].id);
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                patron_id: installations[i].get("patron_id"),
	            });
	        }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: {
                    gcmrkey: "p9wn84m8450yot4ureh",
                    repunch_receivers: repunchReceivers, 
			        action: "com.repunch.consumer.intent.PUNCH",
			        ordered_broadcast: "y",
			        notification_time: String(new Date().getTime()),
			        store_name: storeName,
			        store_id: storeId,
			        punches: numPunches,
                }, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	    
	    return promise;
	}
	
	function executePush(patronStore)
	{
		var punchString = (numPunches == 1) ? "punch" : "punches";
		var promises = [];
		
		promises.push( gcmPost(patronStore) );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
			data: {
				type: "punch",
				"content-available": 1,
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
		punch.set("store_location_id", storeLocationId);
		
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
				console.log("Store save failed.");
				response.error("error");	
				
		}).then(function(employee) {
				if(employee != null) {
					console.log("Employee fetched.");
					employee.relation("Punches").add(punch);
					employee.increment("lifetime_punches", numPunches);
					return employee.save();
				}
				
		}, function(error) {
				console.log("Employee fetch failed.");
				// undo changes above
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
		        postBody.cometrkey = "384ncocoacxpvgrwecwy";
		        Parse.Cloud.httpRequest({
                    method: "POST",
                    url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
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
Parse.Cloud.define("punch_bluetooth", function(request, response)
{
    var numPunches = parseInt(request.params.num_punches);
    var patronId = request.params.patron_id;
    var storeId = request.params.store_id;
    var storeLocationId = request.params.store_location_id;
    var employeeId = request.params.employee_id;

    var Patron = Parse.Object.extend("Patron");
    var PatronStore = Parse.Object.extend("PatronStore");
    var Store = Parse.Object.extend("Store");
    var Employee = Parse.Object.extend("Employee");

    var patronQuery = new Parse.Query(Patron);
    var patronStoreQuery = new Parse.Query(PatronStore);
    var storeQuery = new Parse.Query(Store);

    // Fetch PatronStore
    var patron = new Patron();
    patron.id = patronId;
    var store = new Store();
    store.id = storeId;
    
    patronStoreQuery.equalTo("Patron", patron);
    patronStoreQuery.equalTo("Store", store);
    patronStoreQuery.include("Patron");
    patronStoreQuery.include("Store");

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

    function updatePatronStore(patronStoreResult)
    {
        console.log("updating existing PatronStore");

        patronStoreResult.increment("punch_count", numPunches);
        patronStoreResult.increment("all_time_punches", numPunches);

        patronStoreResult.save().then(function(patronStoreResult) {
            console.log("PatronStore save was successful.");
            saveDataForAnalytics(patronStoreResult, false);

        }, function(error) {
            console.log("PatronStore save failed.");
            response.error("error");
        });
    }

    function addPatronStore()
    {
    	var fetchedPatron, fetchedStore;

        console.log("customer's first punch at this store, adding new PatronStore.");

        var promises = [];
        promises.push( patron.fetch() );
        promises.push( store.fetch() );
    
        Parse.Promise.when(promises).then(function(patronResult, storeResult) {   
            console.log("Store/Patron fetch success (in parallel).");

            fetchedPatron = patronResult;
            fetchedStore = storeResult;

            var patronStore = new PatronStore();
            patronStore.set("punch_count", numPunches);
            patronStore.set("all_time_punches", numPunches);
            patronStore.set("pending_reward", false);
            patronStore.set("Patron", patronResult);
            patronStore.set("Store", storeResult);

            return patronStore.save();

        }, function(error) {
            console.log("Store/Patron fetch fail (in parallel).");

        }).then(function() {
            console.log("PatronStore save success");

            fetchedPatron.relation("PatronStores").add(patronStore);
            fetchedStore.relation("PatronStores").add(patronStore);

            var promises = [];
            promises.push( fetchedPatron.save() );
            promises.push( fetchedStore.save() );

            return Parse.Promise.when(promises);

        }, function(error) {
            console.log("PatronStore save fail");

        }).then(function() {
            console.log("Store and Patron save success (in parallel).");
            saveDataForAnalytics(patronStoreResult, true);

        }, function(error) {
            console.log("Store and Patron save fail (in parallel).");
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
        punch.set("store_location_id", storeLocationId);
        
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
                console.log("Store save failed.");
                response.error("error");    
                
        }).then(function(employee) {
                if(employee != null) {
                    console.log("Employee fetched.");
                    employee.relation("Punches").add(punch);
                    employee.increment("lifetime_punches", numPunches);
                    return employee.save();
                }
                
        }, function(error) {
                console.log("Employee fetch failed.");
                // undo changes above
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
                postBody.cometrkey = "384ncocoacxpvgrwecwy";
                Parse.Cloud.httpRequest({
                    method: "POST",
                    url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
                    headers: { "Content-Type": "application/json"},
                    body: postBody, 
                });
            }
            
            response.success("success");
            
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
	var numPunches = parseInt(request.params.num_punches);
	var storeLocationId = request.params.store_location_id;
	var customerName = request.params.name;
	var messageStatusId = request.params.message_status_id;
	var isOfferOrGift = (messageStatusId != null);
	
	var PatronStore = Parse.Object.extend("PatronStore");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var Store = Parse.Object.extend("Store");
	var Message = Parse.Object.extend("Message");
	
	var redeemReward = new RedeemReward();
	redeemReward.set("store_location_id", storeLocationId);
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
                url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
                headers: {"Content-Type": "application/json"},
                body: { 
                    "cometrkey": "384ncocoacxpvgrwecwy", 
                    pendingRedemption: redeemReward, 
                },
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
            });
            
		});
	}
	
	function gcmPost(){
	    var promise = new Parse.Promise();
	    
	    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
	    var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	    androidInstallationQuery.equalTo("store_id", storeId);
	    androidInstallationQuery.select("registration_id", "employee_id", "support");
	    
	    androidInstallationQuery.find().then(function(installations) {
	        console.log("Found "+installations.length+" employee installations for store_id "+storeId);

	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            console.log("Pushing installation "+installations[i].id);
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                employee_id: installations[i].get("employee_id"),
	            });
	        }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: {
                    gcmrkey: "p9wn84m8450yot4ureh",
                    repunch_receivers: repunchReceivers, 
			        action: "com.repunch.retailer.INTENT_REQUEST_REDEEM",
			        redeem_id: redeemReward.id
                }, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	    
	    return promise;
	}
	
	function executePush() {
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
		iosInstallationQuery.equalTo("store_id", storeId);
	    iosInstallationQuery.equalTo("deviceType", "ios");
	    
	    var promises = [];
	    
	    promises.push( gcmPost() );
	    
		promises.push( Parse.Push.send({
	        where: iosInstallationQuery,
	        data: {
				redeem_id: redeemReward.id,
	            badge: "Increment",
	            type: "request_redeem",
				"content-available": 1
	        }
	    }));
	    
	   Parse.Promise.when(promises).then(function() {
		    console.log("Android/iOS push successful");
			response.success("success");
			
		}, function(error) {
        	console.log("Android/iOS push failed");
			response.error("error");
			
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
// Deletes the RedeemReward, sets the patron store's pending_reward
// to false IF IT IS NOT an offer!
// If RedeemReward does not have a reward_id, then it is an offer, which if it is
// the MessageStatus's redeem_available will be set 'no'.
//
////////////////////////////////////////////////////
Parse.Cloud.define("reject_redeem", function(request, response)
{
	var redeemId = request.params.redeem_id;
	var storeId = request.params.store_id;
	
	// optional - if validated by an employee
	var installationId = request.params.installation_id;
	var androidInstallationId = request.params.android_installation_id;
	
	var Store = Parse.Object.extend("Store");
	var RedeemReward = Parse.Object.extend("RedeemReward");
	var redeemRewardQuery = new Parse.Query(RedeemReward);
	var redeemReward, messageStatus, patronStore, rewardId;
	
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
			
	            if (patronStore != null) {
	                patronStore.set("pending_reward", false);
	                return patronStore.save();
	            } 
	        }
	        
        }, function(error) {
            console.log("Failed to handle MessageStatus.");
            return Parse.Promise.error(error);
	
        }).then(function() {
            return redeemReward.destroy();
            
        }, function(error) {
            console.log("Failed to save PatronStore.");
            return Parse.Promise.error(error);
        
        }).then(function()
            {
            var promises = [];
            
		    var iosEmployeeInstallationQuery = new Parse.Query(Parse.Installation);
		    
		    iosEmployeeInstallationQuery.equalTo("deviceType", "ios");
		    iosEmployeeInstallationQuery.equalTo("store_id", storeId);
		    if (installationId != null) {
		        iosEmployeeInstallationQuery.notEqualTo("objectId", installationId);
		    }
		    
		    // Push to iOS employees
		    promises.push( Parse.Push.send({
	            where: iosEmployeeInstallationQuery,
	            data: {
				    type: "reject_redeem",
				    "content-available": 1,
				    "badge": "decrement",
	                redeem_id: redeemId,
	            }
	        }) );
	        
	        // Post to Android GCM
	        promises.push( gcmEmployeePost() );
            
            // Post to Dashboard
            promises.push(Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
                headers: { "Content-Type": "application/json"},
                body: {
                    "cometrkey": "384ncocoacxpvgrwecwy", 
                    deletedRedemption: redeemReward,
                },
            }));
            
            
		    Parse.Promise.when(promises).then(function() {
                // This is a deleted patronStore if it is not an offer/gift
                // offer/gift do not have a patronStore and reward_id
                if (patronStore == null && rewardId != null)
                    response.error("PATRONSTORE_REMOVED");
                else
                    response.success("success");
		    }, function(error) {
                console.log("Failed to push and/or post to server.");
                response.error(error);
            });
            
        }, function(error) {
            console.log("Failed to destory RedeemReward.");
            response.error(error);
        });
        
    }
    
    function gcmEmployeePost() {
	    var promise = new Parse.Promise();
	    
	    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
	    var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	    androidInstallationQuery.equalTo("store_id", storeId);
	    androidInstallationQuery.select("registration_id", "employee_id", "support");
		if (androidInstallationId != null) {
		    androidInstallationQuery.notEqualTo("objectId", androidInstallationId);
		}
	    
	    androidInstallationQuery.find().then(function(installations) {
	        console.log("Found "+installations.length+" employee installations for store "+storeId);
	        
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	        
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            console.log("Pushing installation "+installations[i].id);
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                employee_id: installations[i].get("employee_id"),
	            });
	        }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: {
                    gcmrkey: "p9wn84m8450yot4ureh",
                    repunch_receivers: repunchReceivers, 
			        action: "com.repunch.retailer.INTENT_REJECT_REDEEM",
			        redeem_id: redeemId,
                }, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	
	    return promise;
	}
    
    function handleMessageStatus(redeemRewardResult) {
        var promise = new Parse.Promise();
	
        redeemReward = redeemRewardResult;
        messageStatus = redeemRewardResult.get("MessageStatus");
        patronStore = redeemRewardResult.get("PatronStore");
        rewardId = redeemRewardResult.get("reward_id")
	
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
// 
//
////////////////////////////////////////////////////
Parse.Cloud.define("validate_redeem", function(request, response)
{
	var redeemId = request.params.redeem_id;
	var storeId = request.params.store_id;
	var rewardId = request.params.reward_id;
	
	// optional - if validated by an employee
	var installationId = request.params.installation_id;
	var androidInstallationId = request.params.android_installation_id;
	
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
						
		} else if(patronStore == null) {
		    redeemReward.destroy().then(function() {
		        response.success({ code:"PATRONSTORE_REMOVED", result: null});
		        postToServerDeleted(redeemReward);
		    });
		
		} else if(patronStore.get("punch_count") < numPunches) {
			console.log("PatronStore has insufficient punches.");
			patronStore.set("pending_reward", false);
			patronStore.save().then(function()
			{
			    console.log("PatronStore save success");
			    
			    redeemReward.destroy().then(function() {
			        postToServerDeleted(redeemReward);
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
	
	function gcmEmployeePost() {
	    var promise = new Parse.Promise();
	    
	    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
	    var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	    androidInstallationQuery.equalTo("store_id", storeId);
	    androidInstallationQuery.select("registration_id", "employee_id", "support");
		if (androidInstallationId != null) {
		    console.log("Excluding Android Installation "+androidInstallationId);
		    androidInstallationQuery.notEqualTo("objectId", androidInstallationId);
		}
	    
	    androidInstallationQuery.find().then(function(installations) {
	        console.log("Found "+installations.length+" employee installations for store "+storeId);
	        
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            console.log("Pushing installation "+installations[i].id);
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                employee_id: installations[i].get("employee_id"),
	            });
	        }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: {
                    gcmrkey: "p9wn84m8450yot4ureh",
                    repunch_receivers: repunchReceivers, 
			        action: "com.repunch.retailer.INTENT_VALIDATE_REDEEM",
			        redeem_id: redeemId,
                }, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	
	    return promise;
	}
	
	function gcmConsumerPost(postBody) {
	    var promise = new Parse.Promise();
	    
	    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
	    var androidInstallationQuery = new Parse.Query(AndroidInstallation);
	    androidInstallationQuery.equalTo("patron_id", patronId);
	    androidInstallationQuery.select("registration_id", "patron_id", "support");
	    
	    androidInstallationQuery.find().then(function(installations) {
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                patron_id: installations[i].get("patron_id"),
	            });
	        }
	        
	        var extendedPostBody = {
                gcmrkey: "p9wn84m8450yot4ureh",
                repunch_receivers: repunchReceivers, 
	            ordered_broadcast: "y",
	            notification_time: String(new Date().getTime()),
            }
            
            for (var i in postBody) {
                extendedPostBody[i] = postBody[i];
            }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: extendedPostBody, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	
	    return promise;
	}
	
	function executePushReward(redeemReward)
	{
		var iosPatronInstallationQuery = new Parse.Query(Parse.Installation);
		var iosEmployeeInstallationQuery = new Parse.Query(Parse.Installation);

		iosPatronInstallationQuery.equalTo("deviceType", "ios");
		iosPatronInstallationQuery.equalTo("patron_id", patronId);
		
		iosEmployeeInstallationQuery.equalTo("deviceType", "ios");
		iosEmployeeInstallationQuery.equalTo("store_id", storeId);
		if (installationId != null) {
		    iosEmployeeInstallationQuery.notEqualTo("objectId", installationId);
		}
		
		var promises = [];
		// Consumer push
	    promises.push( gcmConsumerPost({
	        action: "com.repunch.consumer.intent.VALIDATE_REDEEM_REWARD",
            store_id: storeId,
            store_name: store.get("store_name"),
		    reward_title: rewardTitle,
		    total_punches: patronStore.get("punch_count")
	    })  );
	    
		promises.push( Parse.Push.send({
	        where: iosPatronInstallationQuery,
	        data: {
				type: "redeem",
	            alert: "Redeemed '" + rewardTitle + "'",
	            "content-available": 1,
	            store_id: storeId,
				reward_title: rewardTitle,
				total_punches: patronStore.get("punch_count")
	        }
	    }) );
	    
	    
	    
	    // Employee push
	    promises.push(gcmEmployeePost());
	    
	    promises.push( Parse.Push.send({
	        where: iosEmployeeInstallationQuery,
	        data: {
				type: "validate_redeem",
				"content-available": 1,
				"badge": "decrement",
	            redeem_id: redeemId,
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
		var iosPatronInstallationQuery = new Parse.Query(Parse.Installation);
		var iosEmployeeInstallationQuery = new Parse.Query(Parse.Installation);
		
		iosPatronInstallationQuery.equalTo("patron_id", patronId);
		iosPatronInstallationQuery.equalTo("deviceType", "ios");
		
		iosEmployeeInstallationQuery.equalTo("deviceType", "ios");
		iosEmployeeInstallationQuery.equalTo("store_id", storeId);
		if (installationId != null) {
		    iosEmployeeInstallationQuery.notEqualTo("objectId", installationId);
		}
		
		var promises = [];
		// Consumer push
	    promises.push( gcmConsumerPost({
	        action: "com.repunch.consumer.intent.VALIDATE_REDEEM_OFFERGIFT",
            message_status_id: messageStatus.id,
            store_name: store.get("store_name"),
		    reward_title: rewardTitle,
	    })  );
	    
		promises.push( Parse.Push.send({
	        where: iosPatronInstallationQuery,
	        data: {
				type: "redeem_offer_gift",
				"content-available": 1,
	            alert: "Redeemed '" + rewardTitle + "'",
	            message_status_id: messageStatus.id
	        }
	    }) );

	    // Employee push
	    promises.push(gcmEmployeePost());
	    	    
	    promises.push( Parse.Push.send({
	        where: iosEmployeeInstallationQuery,
	        data: {
				type: "validate_redeem",
				"content-available": 1,
				"badge": "decrement",
	            redeem_id: redeemId,
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
            "cometrkey": "384ncocoacxpvgrwecwy",
	        approvedRedemption: redeemReward,
	    }
	    if(updatedReward != null) {
	        postBody.updatedReward = updatedReward;
	    }
	    Parse.Cloud.httpRequest({
            method: "POST",
            url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: postBody
        });
	}
	
	function postToServerDeleted(redeemReward)
	{
	    Parse.Cloud.httpRequest({
            method: "POST",
            url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: { 
                "cometrkey": "384ncocoacxpvgrwecwy",
                deletedRedemption: redeemReward
            }
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
    // this is provided when the retailer is replying to a feedback
    var feedbackReplyBody = request.params.feedback_reply_body;
    
    var message, receiver_count, redeem_available;
	var patron_ids = new Array(); 
	
	
    var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
    var androidInstallationQuery = new Parse.Query(AndroidInstallation);
    var iosInstallationQuery = new Parse.Query(Parse.Installation);
	iosInstallationQuery.equalTo("deviceType", "ios");
	
	function setMessage(messageResult) {
	    message = messageResult;
        if (message.get("message_type") == "offer") {
            redeem_available = "yes";
        } else {
            redeem_available = "no";
        }
	}

    storeQuery.get(storeId).then(function(storeResult) {
        patronStoreQuery = storeResult.relation("PatronStores").query();
        patronStoreQuery.include("Patron");
        patronStoreQuery.limit(999); 
        return messageQuery.get(messageId);
        
    }, function(error) {
		console.log("Store query failed.");
		response.error("error");
    }).then(function(messageResult) {
        setMessage(messageResult);
        continueWithMessage();
            
    }, function(error) {
        console.log("Message query failed. Retrying...");
        // retry to get the message
        messageQuery.get(messageId).then(function(messageResult) {
            setMessage(messageResult);
            continueWithMessage();
        
        }, function(error) {
            console.log("Message query failed.");
            response.error("error");
            
        });
                
    });
    
    
    function continueWithMessage() {
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
        
    }
    
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
		promises.push( gcmPost() );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
            	type: "message",
            	"content-available": 1,
            	badge: "Increment",
            	alert: storeName + " sent you a message",
                store_id: storeId,
                message_id: messageId
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
	
	function gcmPost(){
	    var promise = new Parse.Promise();
	    
	    androidInstallationQuery.select("registration_id", "patron_id", "support");
	    androidInstallationQuery.find().then(function(installations) {
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                patron_id: installations[i].get("patron_id"),
	            });
	        }
	        
	        var postBody = {
                gcmrkey: "p9wn84m8450yot4ureh",
                repunch_receivers: repunchReceivers, 
		        action: "com.repunch.consumer.intent.RETAILER_MESSAGE",
		        ordered_broadcast: "y",
		        notification_time: String(new Date().getTime()),
                store_name: storeName,
                message_id: messageId,
            }
            
            if (feedbackReplyBody == null) {
                postBody.body_preview = message.get("body").substring(0, 75);
            }
            else
            {
                postBody.body_preview = feedbackReplyBody.substring(0, 75);
            }
            
            if (message.get("subject") != null) {
                postBody.subject = message.get("subject").substring(0, 40);
            }
            
            if (message.get("offer_title") != null) {
                postBody.offer_title = message.get("offer_title");
            }
	    
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: postBody, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	    
	    return promise;
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
		return Parse.Promise.error(error);
				
	}).then(function(store) {
		console.log("Store fetch was successful.");
		store.relation("ReceivedMessages").add(message);
		return store.save();
		
	}, function(error) {
		console.log("Store fetch failed.");
		return Parse.Promise.error(error);
						
	}).then(function(store) {
		console.log("Store save was successful.");
		var patronQuery = new Parse.Query(Patron);
		return patronQuery.get(patronId);
		
	}, function(error) {
		console.log("Store save failed.");
		return Parse.Promise.error(error);
					
	}).then(function(patron) {
		console.log("Patron fetch was successful.");
		patron.relation("SentMessages").add(message);
		return patron.save();	
		
	}, function(error) {
		console.log("Patron fetch failed.");
		return Parse.Promise.error(error);
					
	}).then(function(patron) {
		console.log("Patron save was successful.");
		response.success("success");	
		
	}, function(error) {
		console.log("Patron save failed.");
		response.error("error");
				
	}).then(function() {
	    Parse.Cloud.httpRequest({
            method: "POST",
            url: "http://dev.repunch.com/manage/comet/receive/" + storeId,
            headers: { "Content-Type": "application/json"},
            body: {
                "cometrkey": "384ncocoacxpvgrwecwy", 
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
	
	function gcmPost() {
	    var promise = new Parse.Promise();
	    
        var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
        var androidInstallationQuery = new Parse.Query(AndroidInstallation);
		androidInstallationQuery.equalTo("patron_id", giftRecepientId);
	    androidInstallationQuery.select("registration_id", "patron_id", "support");
	    
	    androidInstallationQuery.find().then(function(installations) {
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                patron_id: installations[i].get("patron_id"),
	            });
	        }
	        
	        var postBody = {
                gcmrkey: "p9wn84m8450yot4ureh",
                repunch_receivers: repunchReceivers, 
		        action: "com.repunch.consumer.intent.SEND_GIFT",
		        ordered_broadcast: "y",
		        notification_time: String(new Date().getTime()),
                sender_name: senderName,
                message_status_id: messageStatus.id,
                gift_title: giftTitle,
                gift_description: giftDescription.substring(0, 75),
            }
            
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: postBody, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	    
	    return promise;
	}
	
	function executePush() {
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
		iosInstallationQuery.equalTo("patron_id", giftRecepientId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( gcmPost() );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
                type: "gift",
                "content-available": 1,
				badge: "Increment",
				alert: senderName + " sent you a gift",
                message_status_id: messageStatus.id
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
	
	function gcmPost() {
	    var promise = new Parse.Promise();
	    
        var AndroidInstallation = Parse.Object.extend("AndroidInstallation");
        var androidInstallationQuery = new Parse.Query(AndroidInstallation);
		androidInstallationQuery.equalTo("patron_id", receiverPatronId);
	    androidInstallationQuery.select("registration_id", "patron_id", "support");
	    
	    androidInstallationQuery.find().then(function(installations) {
	        if(installations.length == 0) {
	            promise.resolve();
	            return;
	        }
	    
	        var repunchReceivers = new Array();
	        for(var i=0; i<installations.length; i++) {
	            repunchReceivers.push({
	                registration_id: installations[i].get("registration_id"),
                    support: installations[i].get("support") == null ? true : installations[i].get("support"),
	                patron_id: installations[i].get("patron_id"),
	            });
	        }
	        
	        var postBody = {
                gcmrkey: "p9wn84m8450yot4ureh",
                repunch_receivers: repunchReceivers, 
		        action: "com.repunch.consumer.intent.REPLY_TO_GIFT",
		        ordered_broadcast: "y",
		        notification_time: String(new Date().getTime()),
                sender_name: senderName,
                message_status_id: messageStatus.id,
                body_preview: body.substring(0, 75),
            }
            
	        Parse.Cloud.httpRequest({
                method: "POST",
                url: "http://dev.repunch.com/gcm/receive",
                headers: { "Content-Type": "application/json"},
                body: postBody, 
                success: function(httpResponse) {
                    console.log("Post success with " + httpResponse.text);
                },
                error: function(httpResponse) {
                    console.error("Request failed with response code " + httpResponse.status);
                }
              
            });
            
            promise.resolve();
            
	    }, function(error) {
	        console.log("error");
	    });
	    
	    
	    return promise;
	}
	
	function executePush() {
		var iosInstallationQuery = new Parse.Query(Parse.Installation);
 
		iosInstallationQuery.equalTo("patron_id", receiverPatronId);
		iosInstallationQuery.equalTo("deviceType", "ios");
		
		var promises = [];
		promises.push( gcmPost() );
		promises.push( Parse.Push.send({
            where: iosInstallationQuery, 
            data: {
                alert: senderName + " replied to your gift",
                message_status_id: messageStatus.id,
                type: "gift_reply",
				badge: "Increment",
				"content-available": 1
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

////////////////////////////////////////////////////
//
//                 Bluetooth Redeem
//
////////////////////////////////////////////////////

// TODO
// HTTP POST needed?
// Error handling
// Facebook Post?

Parse.Cloud.define("redeem_bluetooth", function(request, response)
{
    var storeId = request.params.store_id;
    var patronStoreId = request.params.patron_store_id;
    var rewardId = parseInt(request.params.reward_id);
    var messageStatusId = request.params.message_status_id;

    var Store = Parse.Object.extend("Store");
    var PatronStore = Parse.Object.extend("PatronStore");
    var MessageStatus = Parse.Object.extend("MessageStatus");

    var isOfferOrGift = (messageStatusId != null);

    var store, patron, updatedReward;

    if(isOfferOrGift)
    {
        var messageStatusQuery = new Parse.Query(MessageStatus);
        messageStatusQuery.get(messageStatusId).then(function(messageStatusResult) {
            messageStatusResult.set("redeem_available", "no");
            return messageStatusResult.save();

        }). then(function(messageStatusResult) {
            console.log("MessageStatus save success");
            response.success({ code:"success", result: null });
        });
    }
    else
    {
        var patronStoreQuery = new Parse.Query(PatronStore);
        patronStoreQuery.include("Store");
        patronStoreQuery.include("Patron");
        patronStoreQuery.get(patronStoreId).then(function(patronStoreResult) {

            if(patronStoreResult == null) { // Unlikely for bluetooth but still need to handle
                console.log("PatronStore does not exist.");
                response.success({ code:"PATRONSTORE_REMOVED", result: null});
            }
            else {
                store = patronStoreResult.get("Store");
                patron = patronStoreResult.get("Patron");

                // Update the store's rewards redemption_count
                var rewardsArray = store.get("rewards");
                var punchesToDeduct;

                for (var i = 0; i < rewardsArray.length; i++) {
                    if (rewardsArray[i].reward_id == rewardId) {
                        punchesToDeduct = rewardsArray[i].punches;
                        rewardsArray[i].redemption_count += 1;
                        //updatedReward = {
                        //    redemption_count: rewardsArray[i].redemption_count,
                        //    reward_id: rewardsArray[i].reward_id,
                        //};
                        break;
                    }
                }
            
                if(patronStoreResult.get("punch_count") >= punchesToDeduct) {
                    
                    store.set("rewards", rewardsArray);  // TODO: threading? rewards is shared data.

                    // Update patronStore punch count
                    patronStoreResult.increment("punch_count", -1*punchesToDeduct);

                    var promises = [];
                    promises.push( patronStoreResult.save() );
                    promises.push( store.save() );

                    Parse.Promise.when(promises).then(function(patronStoreResult, storeResult) {   
                        console.log("PatronStore/Store save success (in parallel).");
                        response.success({ code:"success", result: null });

                    }, function(error) {
                        console.log("PatronStore/Store save fail (in parallel).");
                        response.error("error");
                    });
                }
                else {
                    // Not enough punches
                    console.log("PatronStore has insufficient punches.");
                    response.success({ code:"insufficient", result: null });
                }
            }
        }, function(error) {
        	console.log("PatronStore fetch fail.");
        	response.error("error");
        }); //patronStoreQuery
    } //!isOfferOrGift
});


////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("trigger_cloud_logger", function(request, response) {
    
    console.log("Cloud logger is still running.");
    console.log("Extra message: ");
    console.log(request.params.extra_message);
    response.error("error");

});
