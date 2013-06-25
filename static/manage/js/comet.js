/*
    Comet approach.
    constant communication with manage_refresh
*/

$(document).ready(function(){

    var url = $("#comet input[name=comet_url]").val();
    var fakeComet;
    
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

        fakeComet();
    }
    
    function delayedComet(){
        setTimeout(chainComet, 5000);
    }
    
    function chainComet(){
        $.ajax({
            url: url,
            type: "GET",
            timeout: 300000, // 5 mins > serverside request timeout
            success: mainComet,
            // server killed the request but this page is still open
            // so try again after 5 seconds
            error: delayedComet, 
        });
        
    }
    
    fakeComet = chainComet;

    chainComet();

});
