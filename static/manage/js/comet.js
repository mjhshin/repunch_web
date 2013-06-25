/*
    Comet approach.
    constant communication with manage_refresh
*/

// TODO actually implement comet approach
$(document).ready(function(){

    var url = $("#comet input[name=comet_url]").val();
    
    function mainComet(res, status, xhr) {
        // feedback_unread nav
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
        // pending employees nav
        
    }
    
    setInterval(function(){
        $.ajax({
            url: url,
            type: "GET",
            timeout: 300000, // 5 mins > serverside request timeout
            success: mainComet,
        });
    }, 15000);

});
