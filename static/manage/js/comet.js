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
        }        
        // feedbacks while in the Messages page
        
        
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
