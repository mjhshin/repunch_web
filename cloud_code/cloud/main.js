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
Parse.Cloud.define("redeem", function(request, response) {
    var retailerQuery = new Parse.Query(Parse.Installation);
    retailerQuery.equalTo('retailer_id', request.params.retailer_id);
                    
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
    var PatronStore = Parse.Object.extend("PatronStore");
    var patronStoreQuery = new Parse.Query(PatronStore);
    var userQuery = new Parse.Query(Parse.User);
    var installationQuery = new Parse.Query(Parse.Installation);
    var filter = request.params.filter;

    // get a subset of patrons
    if (filter === "all"){
        patronStoreQuery.equalTo("Store", 
            request.params.store_id);
    } else if (filter === "idle") {     
        patronStoreQuery.equalTo("Store", 
            request.params.store_id);
        patronStoreQuery.lessThan("updatedAt", 
            new Date(request.params.idle_date) );
    } else if (filter === "most_loyal") {
        patronStoreQuery.equalTo("Store", 
            request.params.store_id);
        patronStoreQuery.greaterThanOrEqualTo("all_time_punches", 
            request.params.min_punches);
    }  

    // determine the userQuery
    if (filter === "one"){
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
        // match the installation with the username in the 
        // userQuery results
        installationQuery.matchesKeyInQuery("username", "username",
                                                userQuery);
    }

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
