/*
    Comet approach.
    constant communication with comet_refresh
*/

$(document).ready(function(){

    var url = $("#comet_url").val();
    var url_terminate = $("#comet_url_terminate").val();
    var makeRequest; // prototype
    
    String.prototype.trimToDots = function(x){
        if (this.length > x) {
            return this.substring(0, x) + "...";
        } else {
            return this;
        }
    }
    
    // need to have included redemptions.js above this script!   
    
    function mainComet(res, status, xhr) {
        // goes here if there are no changes
        if (res.hasOwnProperty("result")){
            if (res.result == 0){
                makeRequest();
                return;
            } else if (res.result == -1) {
                return;
            }
        } 
        
        // Messages page
        if(res.hasOwnProperty("feedbacks_unread")){
            var feedback_unread_count = new String(res.feedback_unread_count);
            // Messages nav
            var mBadge = $("#messages-nav a div.nav-item-badge");
            var diva = $("#messages-nav a");
            if (mBadge.length == 1){
                mBadge.text(feedback_unread_count);
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    feedback_unread_count + "</div>");
            }
            // tab
            var feedbackTab = $("#tab-feedback");
            if (feedbackTab.length > 0){
                feedbackTab.html("Feedback (" + feedback_unread_count + ")");
                // update the title
                document.title = "Repunch | (" + feedback_unread_count + ") Messages";
            
                // table content
                var feedbacks_unread = res.feedbacks_unread;
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
                // Therefore there is no need to append to a table that is not visible
                if (tabFeedbackActive && (inLastPage||inFirstPage)) {
                    for (var i=0; i<feedbacks_unread.length; i++){
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
                        var d = new Date(feedbacks_unread[i].createdAt);
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
			                feedbacks_unread[i].objectId + "'>" +
				            "<div class='td feedback-date'>"+
                            dStr + "</div>" +
				            "<div class='td feedback-from'>" +
				            feedbacks_unread[i].sender_name.trimToDots(14) + "</div>" +
				            "<div class='td feedback-subject'>" +
				            feedbacks_unread[i].subject.trimToDots(24) + "</div>" +
			                "</a></div>";
			            // prepend if in page 1 and desc
                        if (is_desc && inFirstPage) {
                            row.before(rowStr);
                        // append if in last page and asc
                        } else if (!is_desc && inLastPage) {
                            row.after(rowStr);                
                        }
	                } // end for loop
	                
	                 // remove placeholder when no longer empty
                    if ($("#no-feedback").length > 0) {
                        $("#no-feedback").remove();
                    }
	                
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
	                
	                // update the pagination variables (feedbackPageCount is updated in paginate)
	                feedbackCount.val(parseInt(feedbackCount.val()) + feedbacks_unread.length);
	                
	                // repaginate
                    paginator($("#get-page-url").val(),
                        ["sent", "feedback"], "feedback");                
	                
	            } // end if feedback tab is active
	            
            } // end if in Message page
            
        } // end hasOwnProperty
        
        function addToEmployeesPending(employee) {
            var odd = "";
            var first=$("#tab-body-pending-employees div.tr").first();
            if (!first.hasClass("odd")){
                odd = "odd";
            }
            var d = new Date(employee.createdAt);
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
            $("#tab-body-pending-employees div.table-header").after(
                "<div class='tr " + odd + " unread' id='" + employee.objectId + "' >" +
		        
		        "<div class='td first_name_pending'>" + employee.first_name.trimToDots(12) + "</div>" +
		        "<div class='td last_name_pending'>" + employee.last_name.trimToDots(14) + "</div>" +
		        "<div class='td date_added_pending'>" + dStr + "</div>" +
		        "<div class='td approve'>" +
			    "<a href='/manage/employees/" + employee.objectId + "/approve' class='employee approve'>" +
			        "<img src='/static/manage/images/icon_green-check.png' alt='Approve' /></a>" +
			    "<a href='/manage/employees/" + employee.objectId + "/deny' class='employee deny'>" +
			        "<img src='/static/manage/images/icon_red-x.png' alt='Deny' /></a>" +
		        "</div>" +
		        "</div>" );
        }
        
        function addToEmployeesApproved(employee) {
            var odd = "";
            var first=$("#tab-body-approved-employees div.tr").first();
            if (!first.hasClass("odd")){
                odd = "odd";
            }
            var d = new Date(employee.createdAt);
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
            $("#tab-body-approved-employees div.table-header").after(
                "<div class='tr " + odd + " unread' id='" + employee.objectId + "' >" +
		        
		        "<a href='/manage/employees/" + employee.objectId + "/edit'>" + 
		        "<div class='td first_name_approved'>" + employee.first_name.trimToDots(12) + "</div></a>" +
		        "<a href='/manage/employees/" + employee.objectId + "/edit'>" + 
		        "<div class='td last_name_approved'>" + employee.last_name.trimToDots(14) + "</div></a>" +
		        "<a href='/manage/employees/'" + employee.objectId + "/edit'>" + 
		        "<div class='td date_added_approved'>" + dStr + "</div></a>" +
		        "<a href='/manage/employees/'" + employee.objectId + "/edit'>" + 
		        "<div class='td punches_approved'>" +  new String(employee.lifetime_punches) + "</div></a>" +
		        
				"<div class='td graph'><input type='checkbox' name='employee-graph-cb' value='" + employee.objectId + "' /></div>" + 
				"<div class='td remove'><a href='/manage/employees/" + employee.objectId + "/delete' >" + 
				"<img src='/static/manage/images/icon_red-x.png' alt='Remove' /></a></div>" +
		        
		        "</div>" );
        }
        
        if (res.hasOwnProperty('employees_pending')){
            // pending employees nav
            var employees_pending_count = new String(res.employees_pending_count);
            var mBadge = $("#employees-nav a div.nav-item-badge");
            var diva = $("#employees-nav a");
            if (mBadge.length == 1){
                mBadge.text(employees_pending_count);
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    employees_pending_count + "</div>");
            }
            
            // Employees page
            var pendingTab = $("#tab-pending-employees");
            // tab
            if (pendingTab.length > 0){
                pendingTab.html("Pending (" + 
                            employees_pending_count + ")");
                // update the title
                document.title = "Repunch | (" + employees_pending_count + ") Employees";
                
                // table content
                var employees_pending = res.employees_pending;
                for (var i=0; i<employees_pending.length; i++){
                    addToEmployeesPending(employees_pending[i]);
		        }
		        
                // remove placeholder when empty
                if ($("#no-pending-employees").length > 0){
                    $("#no-pending-employees").remove();
                }
            }
            
        }// end employees pending
        
        function employeesApprovedDeleted(emps, type) {
            // pending employees nav 
            var employees_pending_count = new String(res.employees_pending_count);
            var mBadge = $("#employees-nav a div.nav-item-badge");
            if (mBadge.length == 1) {
                mBadge.text(employees_pending_count);
            } else {
                mBadge.fadeOut(1000, function(){
                    $(this).remove();
                });
            }
            
            // Employees page
            var pendingTab = $("#tab-pending-employees");
            if (pendingTab.length > 0) {
                // move the rows from pending tab to approved tab
                for (var i=0; i< emps.length; i++) {
                    var row = $("#" + emps[i].objectId);
                    // row.css("background", "#FFFFCB");
                    row.css("background", "#CCFF99");
                    if (type == "approved") {
                        // row.html("Employee has been <span style='color:blue;'>APPROVED</span> elsewhere.");
                        row.html("Successfully <span style='color:blue;'>APPROVED</span> employee.");
                    } else {
                        // row.html("Employee has been <span style='color:red;'>DENIED</span> elsewhere.");
                        row.html("Successfully <span style='color:red;'>DENIED</span> employee.");
                    }
                    
                    // the last row to go checks if placeholder is necessary
                    if (i == emps.length - 1) {
                        row.fadeOut(2000, function(){
                            $(this).remove();
                            
                            // place the placeholder if now empty in PENDING
                            if($("#tab-body-pending-employees div.tr").length == 0) {
                                $("#tab-body-pending-employees div.table-header").after(
                                    "<div class='tr' id='no-pending-employees'>" +
                                    "<div class='td'>No Pending Employees</div>" +
                                    "</div>");
                            }
                            
                            // place the placeholder if now empty in APPROVED
                            if($("#tab-body-approved-employees div.tr").length == 0) {
                                $("#tab-body-approved-employees div.table-header").after(
                                    "<div class='tr' id='no-approved-employees'>" +
                                    "<div class='td'>No Approved Employees</div>" +
                                    "</div>");
                            }
                            
                        });
                    } else {
                        row.fadeOut(2000, function(){
                            $(this).remove();
                            // Now add to the approved tab
                            if (type == "approved") {
                                addToEmployeesApproved(emps[i]);
                            }
                        });
                    }
                }
                
                // update the title and the tab
                if (count > 0) {
                    document.title = "Repunch | (" + employees_pending_count + ") Employees";
                    $("#tab-pending-employees").html("Pending (" + employees_pending_count + ")");
                } else {
                    document.title = "Repunch | Employees";
                    $("#tab-pending-employees").html("Pending");
                }
                
            }
            
        }
        
        if (res.hasOwnProperty('employees_approved')){
            employeesApprovedDeleted(res.employees_approved, "approved");
        } 
        if (res.hasOwnProperty('employees_deleted')){
            employeesApprovedDeleted(res.employees_deleted, "deleted");
        } 
        
        // reward redemption count
        if (res.hasOwnProperty('rewards') && res.rewards.length > 0){
            var reSection = $("#rewards");
            // analysis page
            if (reSection.length > 0){
                for (var i=0; i<res.rewards.length; i++){
                    var reward = $("#rewards div.tab-body div.tr#" +  rewards[i].reward_id + " div.td.reward_redemptions");
                    
                 if (reward.length > 0){
                        reward.text(res.rewards[i].redemption_count);
                    }
                }
            }
        }
        
        // incoming redemptions 
        if (res.hasOwnProperty('redemptions_pending')){
            // Workbench nav
            var redemption_pending_count = res.redemption_pending_count;
            var rBadge = $("#redemptions-nav a div.nav-item-badge");
            var diva = $("#redemptions-nav a");
            if (rBadge.length == 1){
                rBadge.text(new String(redemption_pending_count));
            } else {
                diva.append("<div class='nav-item-badge'>" +
                    new String(redemption_pending_count) + "</div>");
            }
        
            // tab
            var pendingTab = $("#tab-pending-redemptions");
            if (pendingTab.length >0){
                pendingTab.html("Pending (" + redemption_pending_count + ")");
                // update the title
                document.title = "Repunch | (" + redemption_pending_count + ") Redemptions";
                
                // table content 
                var redemptions_pending = res.redemptions_pending;
                var pagPage = $("#pag-page");
                var pagThreshold = $("#pag-threshold");
                var pendingCount = $("#pending-redemptions-count");
                var pendingPageCount = $("#pag-page-pending-redemptions-count");
                // only append if we are on the first or last page and if the redemptions tab is the active tab
                var inLastPage = parseInt(pagPage.val()) == parseInt(pendingPageCount.val());
                var inFirstPage = parseInt(pagPage.val()) == 1;
                var tabPendingActive = $("#tab-pending-redemptions").hasClass("active");
                var is_desc = $("#header-redemption_time").hasClass("desc");
                // remember that paginate is called when switching tabs so those rows come from the server!
                // Therefore there is no need to append to a table that is not visible
                if (tabPendingActive && (inLastPage||inFirstPage)) {
                    for (var i=0; i<redemptions_pending.length; i++){
                        var loadingIconUrl = $("#loading_icon_url").val();
                        var greenCheckIconUrl = $("#green_check_url").val();
                        var redXIconUrl = $("#red_x_url").val();
                    
                        var odd = "", row;
                        if (is_desc){
                            row = $("#tab-body-pending-redemptions div.tr").first();
                        } else {
                            row = $("#tab-body-pending-redemptions div.tr").last();
                        }
                        if (!row.hasClass("odd")){
                            odd = "odd";
                        }
                        var d = new Date(redemptions_pending[i].createdAt);
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
                        var rowStr = "<div class='tr " + odd + "' " + 
                            "id='"+ redemptions_pending[i].objectId + "'>" +
		                    "<input type='hidden'" + 
		                    " value='" + redemptions_pending[i].reward_id + "'/>" + 
				            "<div class='td redemption_time'>" +
				            d + "</div>" +
				            "<div class='td redemption_customer_name'>" +
				            redemptions_pending[i].customer_name.trimToDots(16) + "</div>" +
		                    "<div class='td redemption_title'>" +
				            redemptions_pending[i].title.trimToDots(20) + "</div>" +
				            "<div class='td redemption_punches'>" +
				            redemptions_pending[i].num_punches + "</div>" +
				            "<div class='td redemption_redeem' style='margin-top:4px;'>" +
				            
	                        "<a name='" + redemptions_pending[i].objectId + "' style='color:blue;cursor:pointer;'>" +
	                            "<img src='" + greenCheckIconUrl + "' alt='Approve' /></a>" +
	                        "<a name='" + redemptions_pending[i].objectId + "' style='color:blue;cursor:pointer;margin-left:18px;'>" +
	                            "<img src='" + redXIconUrl + "' alt='Deny' /></a>" +
                            "<img src='" + loadingIconUrl + "' alt='processing' " + 
                                "class='redemp-loader' width='18' height='18' />" +
				            
		                    "</div>";
		                // prepend if in page 1 and desc
                        if (is_desc && inFirstPage) {
                            row.before(rowStr);
                        // append if in last page and asc
                        } else if (!is_desc && inLastPage) {
                            row.after(rowStr);                        
                        }   
                    } // end for loop
                    
                    // remove placeholder when not empty
                    if ($("#no-redemptions").length > 0){
                        $("#no-redemptions").remove();
                    }
                    
                    // respect the pagination threshold (trim the last rows that overflow)
                    var rows = $("#tab-body-pending-redemptions div.tr");
                    var rowCount = rows.length;
                    var overflow = parseInt(pagThreshold.val()) - rowCount;
                    if (overflow < 0) {
                        overflow = Math.abs(overflow);
                        while (overflow > 0){
                            rows.last().remove();
                            overflow -= 1;
                        }
                    }
                    
                    // update the pagination variables (pendingPageCount is updated in paginate)
                    pendingCount.val(parseInt(pendingCount.val()) + redemptions_pending.length);
                    
                    // repaginate
                    paginator($("#get-page-url").val(),
                        ["pending-redemptions", "history-redemptions"],
                        "pending-redemptions", rebindRedemptions);      
                    
                } // end if redemption tab is active
                
            } // end if in Workbench page
            
            // Rebind
            rebindRedemptions();
            
        } // end hasOwnProperty
        
        
        function redemptionsApprovedDeleted(redemps, type) {
            
            // Workbench nav
            var redemption_pending_count = res.redemption_pending_count;
            var rBadge = $("#redemptions-nav a div.nav-item-badge");
            if (rBadge.length == 1){
                if (redemption_pending_count > 0) {
                    rBadge.text(new String(redemption_pending_count));
                } else {
                    rBadge.fadeOut(1000, function(){
                        $(this).remove();
                    });
                }
            }
        
            // tab
            var pendingTab = $("#tab-pending-redemptions");
            if (pendingTab.length >0){
                // remove the rows
                for (var i=0; i< redemps.length; i++){
                    var row = $("#" + redemps[i].objectId);
                    // row.css("background", "#FFFFCB");
                    row.css("background", "#CCFF99");
                    if (type == "approved") {
                        // row.html("Redemption has been <span style='color:blue;'>APPROVED</span> elsewhere.");
                        row.html("Successfully <span style='color:blue'>APPROVED</span> redemption.");
                    } else {
                        // row.html("Redemption has been <span style='color:red;'>DENIED</span> elsewhere.");
                        row.html("Successfully <span style='color:red'>DENIED</span> redemption.");
                    }
                    // the last row to go checks if placeholder is necessary
                    if (i == redemps.length - 1) {
                        row.fadeOut(2000, function(){
                            $(this).remove();
                            
                            // place the placeholder if now empty
                            if($("#redemptions-nav a div.nav-item-badge").length == 0) {
                                $("#tab-body-pending-redemptions div.table-header").after(
                                    "<div class='tr' id='no-redemptions'>" +
                                    "<div class='td'>No Redemptions</div>" +
                                    "</div>");
                            }
                        });
                    } else {
                        row.fadeOut(2000, function(){
                            $(this).remove();
                        });
                    }
                }
                
                // update the title and the tab
                if (redemption_pending_count > 0) {
                    document.title = "Repunch | (" + new String(redemption_pending_count) + ") Redemptions";
                    $("#tab-pending-redemptions").html("Pending (" + new String(redemption_pending_count) + ")");
                } else {
                    document.title = "Repunch | Redemptions";
                    $("#tab-pending-redemptions").html("Pending");
                }
                
            }
            
        } 
        
        
        if (res.hasOwnProperty('redemptions_approved')){
            redemptionsApprovedDeleted(res.redemptions_approved, 'approved');
        } 
        
        if (res.hasOwnProperty('redemptions_deleted')){
            redemptionsApprovedDeleted(res.redemptions_deleted, 'deleted');
        } 
        
        if (res.hasOwnProperty('retailer_pin')){
            // Settings page
            var rpin = $("#retailer_pin");
            if (rpin.length > 0){
                rpin.text(res.retailer_pin);
                rpin.addClass('refreshed');
            }
        } // end hasOwnProperty
        
        // establish another connection
        makeRequest();
               
    } // end mainComet
    
    // used serverside as a unique identifier with the session_key
    var timestamp;
    var uid;
    
    var terminateFunc = function() {
        // make a get request to the server flagging to terminate
        // the looping thread associated with this connection 
        $.ajax({
            url: url_terminate,
            type: "GET",
            async: false,
            data: {"timestamp": timestamp, "uid": uid, },
            cache:false, // required to kill internet explorer 304 bug
        });
    };
    
    makeRequest = function() {
        timestamp = (new Date()).toISOString();
        // get a number from 0 to 998 as a unique id just incase they 
        // have 2 tabs refreshing at the same time
        uid = String(Math.floor(Math.random()*999));
        $.ajax({
            url: url,
            type: "GET",
            data: {"timestamp": timestamp, "uid": uid, },
            timeout: 300000, // timeout after 5 minutes! Server must respond before that!
            cache:false, // required to kill internet explorer 304 bug
            success: mainComet,
        });
        
        $(window).unbind("beforeunload", terminateFunc);
        $(window).bind("beforeunload", terminateFunc);
    };
    
    
    // Immediately make a connection
    // IMPORTANT that this is called after server's COMET_DIE_TIME has passed.
    makeRequest();
    

});
