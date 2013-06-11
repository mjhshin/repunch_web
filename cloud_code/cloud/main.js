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
    
    var PatronStore = Parse.Object.extend("PatronStore");
    var patronStoreQuery = Parse.Query(PatronStore);
    var installationQuery = Parse.Query(Parse.Installation);
    var filter = request.params.filter;

    if (filter === "all"){
        patronStoreQuery.equalTo("store_id", 
            request.params.store_id);
    } else if (filter == "idle") {  
        var idleDate = Date();
        // idleDate.set();
        // TODO
        patronStoreQuery.lessThan("updatedAt", idleDate);
    } else if (filter == "most_loyal") {
        patronStoreQuery.greaterThanOrEqualTo("all_time_punches", 
            request.params.min_punches);
    } else {
        response.error("filter");
        return
    }
    
    // step 1: get all of the PatronStores that match the filter
    // step 2: get all of the usernames from the Patron pointer in each PatronStore
    // step 3: prep the installationQuery
    // note that the limit of 1000 parse objects returned per query
    patronStoreQuery.select("username");
    patronStoreQuery.find().then(function(patronStores) {
        var usernames = new Array();
        for (var i=0; i<patronStores.length; i++){
            usernames.push();
            
        }

        installationQuery.containedIn("username", usernames);
        Parse.Push.send({
            where:installationQuery, 
            data: {
                alert: "New message from " + request.params.store_name,
                subject: request.params.subject,
                body: request.params.body,
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

    }); // end patronStoreQuery
 
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
