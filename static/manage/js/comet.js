/*
    Comet approach.
    constant communication with manage_refresh
*/



// TODO actually implement comet approach
$(document).ready(function(){

    var url = $("#comet input[name=comet_url]").val();
    
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
                feedbackTab.html("Feedback (" + 
                            new String(res.feedback_unread) + ")");
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
                    new String(res.employees_peding) + "</div>");
            }
        }         
               
    }
    
    function startLoop(){
        setInterval(function(){
            $.ajax({
                url: url,
                type: "GET",
                success: mainComet,
            });
        }, 10000);
    }
    
    // make the initial call and set the interval here!
    $.ajax({
        url: url,
        type: "GET",
        success: startLoop,
    });

});
