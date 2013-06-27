/*
    Script for everythin in the dialog-logjn box.
*/

// TODO clean up code lol
$(document).ready(function(){

    var dl = $( "#dialog-login" );
    var loadingHeight = 10;
    var fpdiv = $("#forgot-pass-form-div");
    
    // PASSWORD RESET
    $("#forgot-pass-form a").click(function(){
        if (fpdiv.css("display") != "none"){
            return;
        }
        // adjust the height
        dl.dialog( "option", "height", dl.dialog( "option", "height") + 20 );
        // show the input
        fpdiv.fadeIn(1000);
        
    });
    
    $("#forgot-pass-form input[type=submit]").click(function(){
        // make the ajax call
        $.post($("#forgot-pass-form input[name=action]").val(), 
                    $("#forgot-pass-form").serialize(), function(res){
            if (res.res){
                $("#forgot-pass-form").html("<span style='color:green;'>Password Reset form sent.</span>");
            } else {
                $("#forgot-pass-form a").html("<span>Email not recognized.</span>");
            }
        }).fail(function(){ // should not go here unless server error
            fpdiv.html("<span>Email not recognized.</span>");
        });
        return false;
    });
    
    // LOGIN
    $("#dialog-login-form input[type=submit]").click(function(){
    
        var loading = $("#logging-in");
        // prevent multiple button clicks
        if (loading.css("display") != "none"){
            return false;
        }
        // show the loading indicator
        dl.dialog( "option", "height", dl.dialog( "option", "height") + loadingHeight );
        loading.show();
        
        var url = $("#dialog-login input[name=action]").val();
        var url_redirect = $("#dialog-login-form input[name=redirect-url]").val();
        var data = $("#dialog-login-form").serialize();
        
        var messageContainer = $("#dialog-login-message");
        
        function finish(dim){
            if (fpdiv.css("display") != "none"){
                dl.dialog( "option", "height", dim + 30 );
            } else {
                dl.dialog( "option", "height", dim );
            }
        }
        
        // make the login request to the server
        // if success, redirect to store index page
        // if not active or wrong password, message pops up.
        $.post(url, data, function(res) {
            /* result codes
               -1 - invalid request
                0 - invalid form input
                1 - bad login credentials
                2 - subscription is not active
                3 - success */
            if (res.code == 3){
                window.location.replace(url_redirect);
                finish(320);
            } else if (res.code == 2){
                messageContainer.html("<span>Your account is not yet active.<br/>" +
                                " We will get in touch with you soon.</span>");
                finish(340);
                loading.hide();
            } else if (res.code == 1){
                messageContainer.html("<span>The username or password you entered is incorrect.</span>");
                finish(340);
                loading.hide();
            } else {
                // same as 1 but may want to change later
                messageContainer.html("<span>The username or password you entered is incorrect.</span>");
                finish(340);
                loading.hide();
            }
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
            finish(320);
            loading.hide();
        });
        
        return false;
    });
    
});
