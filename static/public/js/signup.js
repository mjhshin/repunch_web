/*
    Signup routine script.
*/

$(document).ready(function(){

    $( "#dialog-signup" ).dialog({ autoOpen: false, modal: true, 
        title: "Signing up",
        resizable: false,
        minWidth: 330, minHeight: 100,
        maxWidth: 330, maxHeight: 100, });

    var messageContainer = $("#dialog-signup-message");
    $("#signup-form-submit").click(function(){
        // open the dialog with the loading message
        $( "#dialog-signup" ).dialog( "open" );
        // make sure the time icon is hidden
        $("#signing-up-time").hide();
        
        // make the ajax call
        var url = $("#signup-form input[name=action]").val();
        var url_redirect = $("#signup-form input[name=redirect-url]").val();
        var url_home = $("#signup-form input[name=home-url]").val();
        
        var data = $("#signup-form").serialize();
        $.post(url, data, function(res, status, xhr) {
            $("#signing-up").hide();
            respType = xhr.getResponseHeader("content-type");
            
            if (respType.indexOf("html") != -1){
                // form had errors, replace entire page
                var newDoc = document.open("text/html", "replace");
                newDoc.write(res);
                newDoc.close();
                $( "#dialog-signup" ).dialog( "close" );
            } else if (respType.indexOf("json") != -1){
                if (res.code == 2){
                    // subscription not active. Tell them.
                    $( "#dialog-signup" ).dialog({ 
                        minHeight: 95, maxHeight: 95,
                        close: function(){
                            window.location.replace(url_home);
                        } });
                    $("#signing-up-time").show();
                    messageContainer.html("<span style='color:#DF7401;position:relative;top:4px;'>"+
                        "Your account is not yet active.<br/>We will get in touch with you soon.</span>");
                }
                // active subscription. redirect to dashboard.
                else if (res.code == 3){
                    messageContainer.html("<span style='color:green;'>Redirecting to dashboard.</span>");
                    window.location.replace(url_redirect);
                }
            }
            
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
        });
        
        return false;
    });
    
});
