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
    var userQuery = new Parse.Query(Parse.Installation);
    userQuery.equalTo('punch_code', request.params.punch_code);
                    
    Parse.Push.send({
        where: userQuery,
        data: {
            name: request.params.retailer_name,
            id: request.params.retailer_id,
            num_punches: request.params.num_punches,
            action: "com.repunch.intent.PUNCH"
        }
    }, {
        success: function() {
        	// Push was successful
			var patron = Parse.Object.extend("Patron");
			var patronQuery = new Parse.Query(patron);
			query.equalTo("punch_code", request.params.punch_code);
		
			var patronStore = Parse.Object.extend("PatronStore");
			var patronStoreQuery = new Parse.Query(patronStore);
			patronStoreQuery.whereMatchesKeyInQuery("Patron.objectId", "objectId", patronQuery);
			patronStoreQuery.first({
				success: function(object) {
					if(object != null) { 
						object.increment("punch_count", request.params.num_punches);
						object.increment("all_time_punches", request.params.num_punches);
						object.save(null, {
							success: function(object) {
								response.success("success");
							},
							error: function(object, error) {
								response.error("error");
							}
						});
					} else { //need to create new PatronStore entry
						//response.error("error");
						var PatronStore = Parse.Object.extend("PatronStore");
						var patronStore = new PatronStore();
						patronStore.put("punch_count", request.params.num_punches);
						patronStore.put("all_time_punches", request.params.num_punches);
						patronStore.save(null, {
							success: function(object) {
								response.success("success");
							},
							error: function(object, error) {
								response.error("error");
							}
						});
					}
				},
				error: function(error) {
					response.error("error");
				}
			});
        },
        error: function(error) {
			response.error("error");
        }
    });
});
 
////////////////////////////////////////////////////
//
//
//
////////////////////////////////////////////////////
Parse.Cloud.define("redeem", function(request, response) {
    var retailerQuery = new Parse.Query(Parse.Installation);
    retailerQuery.equalTo('store_id', request.params.retailer_id);
                    
    Parse.Push.send({
        where: retailerQuery,
        data: {
            alert: request.params.name + " wants to redeem a reward.",
            badge: "Increment",
            name: request.params.name,
            username: request.params.username,
            num_punches: request.params.num_punches,
            title: request.params.title,
            description: request.params.description
        }
    }, {
        success: function() {
            // Push was successful
            response.success("success");
        },
        error: function(error) {
            // Handle error
            response.error("error");
        }
    });
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
    var messageQuery = new Parse.Query(Message);
    var patronStoreQuery = new Parse.Query(PatronStore);
    var installationQuery = new Parse.Query(Parse.Installation);
    var userQuery = new Parse.Query(Parse.User);
    var filter = request.params.filter;
    var message; // placeholder

    function addToPatronInbox(username) {
        // add message to the patron's ReceivedMessages relation
        // first we must get the user
        console.log("ADD TO PATRON INBOX FOR " + username);
        var uq = new Parse.Query(Parse.User);
        uq.equalTo("username", username);
        uq.first().then(function(user){
            // then get the Patron pointed to by the user
            console.log("ADD TO PATRON INBOX FOR " + username + " 2nd.");
            var pt = user.get("Patron");
            console.log("NOW FETCHING PATRON FOR USER " + user.get("username"));
            pt.fetch({
                success: function(pt){
                    console.log(pt.get("gender"));
                    var rel = pt.relation("ReceivedMessages");
                    // message obtained from the beginning (bottom)
                    rel.add(message);
                    pt.save();
                }, // end success function
                error: function(pt, error){
                    response.error(error);
                    console.log("ERROR IN FETCHING PATRON.");
                    console.log(error);
                }
            }); // end patron fetch
        }); // end uq 
    }

    // class when all tasks are done
    function proceedToPush(){
        console.log("PROCEED TO PUSH");
        Parse.Push.send({
            where:installationQuery, 
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

        // determine the userQuery
        if (filter === "one"){
            addToPatronInbox(request.params.username);
            // the below will proceed to excute while the userQuery
            // above executes but it shouldn't matter

            // store replies to a feedback
            installationQuery.equalTo("username", 
                                request.params.username);
        } else {
            // store sends a message
            patronStoreQuery.select("Patron");
            userQuery.equalTo("account_type", "patron");
            userQuery.matchesKeyInQuery("Patron", "Patron",
                        patronStoreQuery);
            userQuery.select("username");

            // adding relation to all patron's ReceivedMessages
            userQuery.find().then(function(users){
                for (var i=0; i<users.length; i++){
                    addToPatronInbox(users[i].get("username"));
                }
            }).then(function(){
                // match the installation with the username in the 
                // userQuery results
                installationQuery.matchesKeyInQuery("username", 
                                    "username", userQuery);
                // all tasks are done. Push now.
                proceedToPush();
            });;// end userQuery
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
