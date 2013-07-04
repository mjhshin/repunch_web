/*
    Comet approach.
    constant communication with comet_refresh
*/

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
                if (res.result == 1 || res.result == 2){
                    if (res.result == 1){
                        row.css("background", "#CCFF99");
                        row.html("Successfully validated redemption.");
                    } else {
                        row.css("background", "#ffffcb");
                        row.html("Customer does not have enough punches!");
                        alert("Customer does not have enough punches!");
                    }
                    row.fadeOut(2000, function(){
                        // no longer necessary to append to past redemptions since
                        // clicking on redeem means that the redemption tab is active...
                        
                        // then remove
                        $(this).remove();
                                                
                        // update the counts
                        var rBadge = $("#redemptions-nav a div.nav-item-badge");
                        var diva = $("#redemptions-nav a");
                        var rcount = new String($("#tab-body-pending-redemptions div.tr").length);
                        if (rcount < 1){
                            // workbench nav badge
                            if (rBadge.length == 1){
                                rBadge.fadeOut(2000);
                            }
                            
                            // pending tab
                            $("#tab-pending-redemptions").html("Pending");
                            
                            // place the placeholder if now empty
                            $("#tab-body-pending-redemptions div.table-header").after(
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
    $("#tab-body-pending-redemptions div.tr div.td a").click(function(){
        onRedeem($(this).attr("name"));
    });
    
    function mainComet(res, status, xhr) {
        // goes here if there are no changes
        if (res.hasOwnProperty("result")){
            if (res.result == 0){
                return;
            }
        }
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
                // update the title
                document.title = "Repunch | (" + feedback_unread + ") Messages";
            
                // table content
                var feedbacks = res.feedbacks;
                var pagPage = $("#pag-page");
                var pagThreshold = $("#pag-threshold");
                var feedbackCount = $("#feedback-count");
                var feedbackPageCount = $("#pag-page-feedback-count");
                // only append if we are on the first or last page and if the feedbacks tab is the active tab
                var inLastPage = parseInt(pagPage.val()) == parseInt(feedbackPageCount.val());
                var inFirstPage = parseInt(pagPage.val()) == 1;
                var tabFeedbackActive = $("#tab-feedback").hasClass("active");
                var is_desc = $("#header-feedback-date").hasClass("desc");
                // remember that paginate is called when switching tabs so those rows come from the server!
                if (tabFeedbackActive && (inLastPage||inFirstPage)) {
                    for (var i=0; i<feedbacks.length; i++){
                        // determine if date is asc or desc
                        var odd = "", row;
                        if (is_desc){
                            row = $("#tab-body-feedback div.tr").first();
                        } else {
                            row = $("#tab-body-feedback div.tr").last();
                        }
                        if (!row.hasClass("odd")){
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
                        if (day.length == 1) {
                            day = "0" + day;
                        }
                        var dStr = month + "/" + day + "/" + year;
                        var rowStr = "<div class='tr " + odd + " unread'>" +
			                "<a href='/manage/messages/feedback/" + 
			                feedbacks[i].objectId + "'>" +
				            "<div class='td feedback-date'>"+
                            dStr + "</div>" +
				            "<div class='td feedback-from'>" +
				            feedbacks[i].sender_name + "</div>" +
				            "<div class='td feedback-subject'>" +
				            feedbacks[i].subject + "</div>" +
			                "</a></div>";
			            // prepend if in page 1 and desc
                        if (is_desc && inFirstPage) {
                            row.before(rowStr);
                        // append if in last page and asc
                        } else if (!is_desc && inLastPage) {
                            row.after(rowStr);                        
                        }
	                } // end for loop
	                
	                // update the pagination variables (feedbackPageCount is updated in paginate)
	                feedbackCount.val(feedbacks.length + parseInt(feedbackCount.val()));
	                // respect the pagination threshold (trim the last rows that overflow)
	                var rows = $("#tab-body-feedback div.tr");
	                var rowCount = rows.length;
	                var overflow = parseInt(pagThreshold.val()) - rowCount;
	                if (overflow < 0) {
	                    overflow = Math.abs(overflow);
	                    while (overflow > 0){
	                        rows.last().remove();
	                        overflow -= 1;
	                    }
	                }
	                
	                // repaginate
                    paginator($("#get-page-url").val(), ["sent", "feedback"], "feedback");                
	                
	            } // end if feedback tab is active
	            
                // remove placeholder when no longer empty
                if ($("#no-feedback").length > 0) {
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
            // tab
            if (pendingTab.length > 0){
                pendingTab.html("Pending (" + 
                            employees_pending + ")");
                // update the title
                document.title = "Repunch | (" + employees_pending + ") Employees";
                
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
        
        // incoming redemptions TODO asc/desc
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
            // tab
            if (pendingTab.length >0){
                pendingTab.html("Pending (" + redemption_count + ")");
                // update the title
                document.title = "Repunch | (" + redemption_count + ") Redemptions";
                
                // table content TODO
                var redemptions = res.redemptions;
                var pagPage = $("#pag-page");
                var pagThreshold = $("#pag-threshold");
                var pendingCount = $("#pending-redemptions-count");
                var pendingPageCount = $("#pag-page-pending-redemptions-count");
                // only append if we are on the first or last page and if the redemptions tab is the active tab
                var inLastPage = parseInt(pagPage.val()) == parseInt(redemptionPageCount.val());
                var inFirstPage = parseInt(pagPage.val()) == 1;
                var tabPendingActive = $("#tab-pending-redemptions").hasClass("active");
                var is_desc = $("#header-redemption_time").hasClass("desc");
                // remember that paginate is called when switching tabs so those rows come from the server!
                for (var i=0; i<redemptions.length; i++){
                    var odd = "", x=$("#tab-body-pending-redemptions div.tr").first();
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
            $("#tab-body-pending-redemptions div.tr div.td a").click(function(){
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
