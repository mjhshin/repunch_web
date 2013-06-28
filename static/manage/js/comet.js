/*
    Comet approach.
    constant communication with manage_refresh
*/


// TODO actually implement comet approach
// TODO cleanup code (appending to pending and present same code!)
$(document).ready(function(){

    var url = $("#comet_url").val();
    var urlRedeem = $("#redeem-url").val();
    
    // for the workbench page
    function onRedeem(rowId){
        var row = $("#" + rowId);
        var rewardId = $("#" + rowId + " input[type=hidden]").val();
        var customerName = $("#" + rowId + " div:nth-child(3)").text();
        var title = $("#" + rowId + " div:nth-child(4)").text();
        var numPunches = $("#" + rowId + " div:nth-child(5)").text();
        $.ajax({
            url: urlRedeem,
            data: {"redeemRewardId":rowId,
                    "rewardId":rewardId }, 
            type: "GET",
            success: function(res){
                if (res.result == 1){
                    row.css("background", "#CCFF99");
                    row.html("Successfully validated redemption.");
                    row.fadeOut(3000, function(){
                        // append to past
                        var odd = "", 
                            x=$("#redemption-past div.tab-body div.tr").first();
                        if (!x.hasClass("odd")){
                            odd = "odd";
                        }
                        var d = new Date();
                        var hour = d.getHours();
                        var minute = new String(d.getMinutes());
                        var ampm;
                        if (hour > 12){
                            ampm = "p.m.";
                        } else {
                            ampm = "a.m.";
                        }
                        if (hour > 12){
                            hour = hour - 12;
                        }
                        hour = new String(hour);
                        if (hour.length < 2){
                            hour = "0" + hour;
                        }
                        if (minute.length < 2){
                            minute = "0" + minute;
                        }
                        d = hour + ":" + minute + " " + ampm;
                        var content = "<div class='tr " + odd + "' " + 
                            "id='"+ rowId + "'>" +
		                    "<input type='hidden'" + 
		                    " value='" + rewardId + "'/>" + 
				            "<div class='td redemption_time-past'>" +
				            d + "</div>" +
				            "<div class='td redemption_customer_name-past'>" +
				            customerName + "</div>" +
		                    "<div class='td redemption_title-past'>" +
				            title + "</div>" +
				            "<div class='td redemption_punches-past'>" +
				            numPunches + "</div>" +
				            "<div class='td redemption_redeem-past'>" +
				            "</div>" +
		                    "</div>";
		                x.before(content);
                        
                        // then remove
                        $(this).remove();
                                                
                        // update the counts
                        var rBadge = $("#redemptions-nav a div.nav-item-badge");
                        var diva = $("#redemptions-nav a");
                        var rcount = new String($("#redemption div.tab-body div.tr").length);
                        if (rcount < 1){
                            // workbench nav badge
                            if (rBadge.length == 1){
                                rBadge.fadeOut('slow');
                            }
                            
                            // pending tab
                            $("#tab-pending-redemptions").html("Pending");
                            
                            // place the placeholder if now empty
                            $("#redemption div.tab-body div.table-header").after(
                                "<div class='tr' id='no-redemptions'>" +
				                "<div class='td'>No Redemptions</div>" +
			                    "</div>");
                        } else {
                            // workbench nav badge
                            if (rBadge.length == 1){
                                rBadge.text(rcount);
                            } else {
                                diva.append("<div class='nav-item-badge'>" +
                                    rcount + "</div>");
                            }
                            
                            // pending tab
                            $("#tab-pending-redemptions").html("Pending (" + rcount + ")");
                            
                        }
                        
                    });
                } else {
                    alert("Redemption failed");
                }
            },
            error: function(res){
                // TODO
            },
        });
    }
    
    // bind
    $("#redemption div.tr div.td a").click(function(){
        onRedeem($(this).attr("name"));
    });
    
    function mainComet(res, status, xhr) {
        // Messages page
        if(res.hasOwnProperty("feedbacks")){
            var feedback_unread = new String(res.feedback_unread);
            // Messages nav
            var mBadge = $("#messages-nav a div.nav-item-badge");
            var diva = $("#messages-nav a");
            if (mBadge.length == 1){
                mBadge.text(feedback_unread);
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    feedback_unread + "</div>");
            }
            // tab
            var feedbackTab = $("#tab-feedback");
            if (feedbackTab.length > 0){
                feedbackTab.html("Feedback (" + feedback_unread + ")");
            
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
	            
                // remove placeholder when empty
                if ($("#no-feedback").length > 0){
                    $("#no-feedback").remove();
                }
            }
            
        } 
        
        if (res.hasOwnProperty('employees')){
            // pending employees nav
            var employees_pending = new String(res.employees_pending);
            var mBadge = $("#employees-nav a div.nav-item-badge");
            var diva = $("#employees-nav a");
            if (mBadge.length == 1){
                mBadge.text(employees_pending);
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    employees_pending + "</div>");
            }
            
            // Employees page
            var pendingTab = $("#tab-pending");
            if (pendingTab.length > 0){
                // tab
                pendingTab.html("Pending (" + 
                            employees_pending + ")");
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
		        
                // remove placeholder when empty
                if ($("#no-pending").length > 0){
                    $("#no-pending").remove();
                }
            }
            
        }// end employees
        
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
        if (res.hasOwnProperty('redemptions')){
            // Workbench nav
            var redemption_count = res.redemption_count;
            var rBadge = $("#redemptions-nav a div.nav-item-badge");
            var diva = $("#redemptions-nav a");
            if (rBadge.length == 1){
                rBadge.text(new String(redemption_count));
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    new String(redemption_count) + "</div>");
            }
        
            // workbench page
            var pendingTab = $("#tab-pending-redemptions");
            if (pendingTab.length >0){
                // tab
                pendingTab.html("Pending (" + redemption_count + ")");
                
                // table content
                var redemptions = res.redemptions;
                for (var i=0; i<redemptions.length; i++){
                    var odd = "", x=$("#redemption div.tab-body div.tr").first();
                    if (!x.hasClass("odd")){
                        odd = "odd";
                    }
                    var d = new Date(redemptions[i].createdAt);
                    var hour = d.getHours();
                    var minute = new String(d.getMinutes());
                    var ampm;
                    if (hour > 12){
                        ampm = "p.m.";
                    } else {
                        ampm = "a.m.";
                    }
                    if (hour > 12){
                        hour = hour - 12;
                    }
                    hour = new String(hour);
                    if (hour.length < 2){
                        hour = "0" + hour;
                    }
                    if (minute.length < 2){
                        minute = "0" + minute;
                    }
                    d = hour + ":" + minute + " " + ampm;
                    var content = "<div class='tr " + odd + "' " + 
                        "id='"+ redemptions[i].objectId+ "'>" +
		                "<input type='hidden'" + 
		                " value='" + redemptions[i].reward_id + "'/>" + 
				        "<div class='td redemption_time'>" +
				        d + "</div>" +
				        "<div class='td redemption_customer_name'>" +
				        redemptions[i].customer_name + "</div>" +
		                "<div class='td redemption_title'>" +
				        redemptions[i].title + "</div>" +
				        "<div class='td redemption_punches'>" +
				        redemptions[i].num_punches + "</div>" +
				        "<div class='td redemption_redeem'>" +
				        "<a name='" + redemptions[i].objectId +
				            "' style='color:blue;cursor:pointer;'>redeem</a></div>" +
		                "</div>";
		            x.before(content);   
                }
                
                // remove placeholder when empty
                if ($("#no-redemptions").length > 0){
                    $("#no-redemptions").remove();
                }
                
            }
            
            // bind
            $("#redemption div.tr div.td a").click(function(){
                onRedeem($(this).attr("name"));
            });
            
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
