/*
    Comet approach.
    constant communication with manage_refresh
*/



// TODO actually implement comet approach
$(document).ready(function(){

    var url = $("#comet_url").val();
    
    // TODO on click redeem function & initial bind
    
    function mainComet(res, status, xhr) {
        // Messages nav
        if (res.hasOwnProperty('feedback_unread')){
            var mBadge = $("#messages-nav a div.nav-item-badge");
            var diva = $("#messages-nav a");
            if (mBadge.length == 1){
                mBadge.text(new String(res.feedback_unread));
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    new String(res.feedback_unread) + "</div>");
            }
            
            // Messages page
            var feedbackTab = $("#tab-feedback");
            if (feedbackTab.length > 0){
                // tab
                feedbackTab.html("Feedback (" + 
                            new String(res.feedback_unread) + ")");
                // remove placeholder when empty
                if ($("#no-feedback").length > 0){
                    $("#no-feedback").remove();
                }
                // table content
                var feedbacks = res.feedbacks;
                for (var i=0; i<feedbacks.length; i++){
                    var odd = "";
                    var first=$("#tab-body-feedback div.tr").first();
                    if (!first.hasClass("odd")){
                        odd = "odd";
                    }
                    var d = new Date(feedbacks[i].createdAt);
                    var year = new String(d.getYear());
                    year = year.substring(1, year.length);
                    var month = new String(d.getMonth()+1);
                    if (month.length == 1){
                        month = "0" + month;
                    }
                    var day = new String(d.getDate());
                    if (day.length == 1){
                        day = "0" + day;
                    }
                    var dStr = month + "/" + day + "/" + year;
                    $("#tab-body-feedback div.table-header").after(
                        "<div class='tr " + odd + " unread'>" +
				        "<a href='/manage/messages/feedback/" + 
				        feedbacks[i].objectId + "'>" +
					    "<div class='td feedback-date'>"+
                        dStr + "</div>" +
					    "<div class='td feedback-from'>" +
					    feedbacks[i].sender_name + "</div>" +
					    "<div class='td feedback-subject'>" +
					    feedbacks[i].subject + "</div>" +
				        "</a></div>" );
		        }
            }
        } 
        
        // pending employees nav
        if (res.hasOwnProperty('employees_pending')){
            var mBadge = $("#employees-nav a div.nav-item-badge");
            var diva = $("#employees-nav a");
            if (mBadge.length == 1){
                mBadge.text(new String(res.employees_pending));
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    new String(res.employees_pending) + "</div>");
            }
            
            // Employees page
            var pendingTab = $("#tab-pending");
            if (pendingTab.length > 0){
                // notification header
                var notific = $("#notification-pending");
                if (notific.length > 0){
                    var s = "";
                    if (res.employees_pending > 1){s="s";}
                    notific.html("<div>You have " +
                        res.employees_pending + 
                        " employee" + s + " pending approval</div>");
                }
                // tab
                pendingTab.html("Pending (" + 
                            new String(res.employees_pending) + ")");
                // remove placeholder when empty
                if ($("#no-pending").length > 0){
                    $("#no-pending").remove();
                }
                // table content
                var employees = res.employees;
                for (var i=0; i<employees.length; i++){
                    var odd = "";
                    var first=$("#tab-body-pending div.tr").first();
                    if (!first.hasClass("odd")){
                        odd = "odd";
                    }
                    var d = new Date(employees[i].createdAt);
                    var year = new String(d.getYear());
                    year = year.substring(1, year.length);
                    var month = new String(d.getMonth()+1);
                    if (month.length == 1){
                        month = "0" + month;
                    }
                    var day = new String(d.getDate());
                    if (day.length == 1){
                        day = "0" + day;
                    }
                    var dStr = month + "/" + day + "/" + year;
                    $("#tab-body-pending div.table-header").after(
                        "<div class='tr " + odd + " unread'>" +
				        
				        "<div class='td first_name_pending'>" + employees[i].first_name + "</div>" +
				        "<div class='td last_name_pending'>" + employees[i].last_name + "</div>" +
				        "<div class='td date_added_pending'>" + dStr + "</div>" +
				        "<div class='td approve'>" +
					    "<a href='/manage/employees/" + employees[i].objectId + "/approve' class='employee approve'>" +
					        "<img src='/static/manage/images/icon_green-check.png' alt='Approve' /></a>" +
					    "<a href='/manage/employees/" + employees[i].objectId + "/deny' class='employee deny'>" +
					        "<img src='/static/manage/images/icon_red-x.png' alt='Deny' /></a>" +
				        "</div>" +
				        "</div>" );
		        }
            }
            
        }// end pending employees nav
        
        // reward redemption count
        if (res.hasOwnProperty('rewards') && res.rewards.length > 0){
            var reSection = $("#rewards");
            // analysis page
            if (reSection.length > 0){
                for (var i=0; i<res.rewards.length; i++){
                    var reward = $("#rewards div.tab-body div.tr div.td.reward_name").filter(function(){return $(this).text() == res.rewards[i].reward_name;});
                    
                 if (reward.length > 0){
                  reward.next().text(res.rewards[i].redemption_count);
                    }
                }
            }
        }
        
        // incoming redemptions
        if (res.hasOwnProperty('redemptions') &&
                res.redemptions.length > 0){
            // remove placeholder when empty
            if ($("#no-redemptions").length > 0){
                $("#no-redemptions").remove();
            }
            // workbench page
            var redemptions = res.redemptions;
            for (var i=0; i<redemptions.length; i++){
                var odd = "";
	            // TODO check if asc or desc
                var x=$("#redemption div.tab-body div.tr").first();
                if (!x.hasClass("odd")){
                    odd = "odd";
                }
                $("#redemption div.tab-body div.table-header").after(
                    "<div class='tr " + odd + "'>" +
				    "<div class='td redemption_customer_name'>" +
				    redemptions[i].customer_name + "</div>" +
		            "<div class='td redemption_title'>" +
				    redemptions[i].title + "</div>" +
				    "<div class='td redemption_punches'>" +
				    redemptions[i].num_punches + "</div>" +
				    "<div class='td redemption_redeem'>" +
				    // TODO button
		            "</div>" );
            }
            
            // TODO rebind on click function
            
            // remove the last if greater than 40
	      // while ($("#redemption div.tab-body div.tr").length > 40){
	            // TODO check if asc or desc
	         //$("#redemption div.tab-body div.tr").last().remove();
	        //}
        }
               
    } // end mainComet
    
    setInterval(function(){
        $.ajax({
            url: url,
            type: "GET",
            success: mainComet,
        });
    }, 10000);

});
