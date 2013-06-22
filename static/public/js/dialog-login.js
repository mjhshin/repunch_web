/*
    Script for everythin in the dialog-logjn box.
*/

$(document).ready(function(){

    $("#dialog-login-form input[type=submit]").click(function(){
    
        var loading = $("#logging-in");
        // prevent multiple button clicks
        if (loading.css("display") != "none"){
            return false;
        }
        // show the loading indicator
        loading.show();
        
        var url = $("#dialog-login input[name=action]").val();
        var url_redirect = $("#dialog-login-form input[name=redirect-url]").val();
        var data = $("#dialog-login-form").serialize();
        
        var messageContainer = $("#dialog-login-message");
        
        function finish(dim){
            $( "#dialog-login" ).dialog({
	        minHeight: dim, maxHeight: dim, });
            loading.hide();
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
                messageContainer.html("<span style='color:green;'>Redirecting to dashboard.</span>");
                window.location.replace(url_redirect);
                finish(310);
            } else if (res.code == 2){
                messageContainer.html("<span>Your account is not yet active.<br/>" +
                                " We will get in touch with you soon.</span>");
                finish(330);
            } else if (res.code == 1){
                messageContainer.html("<span>The username or password you entered is incorrect.</span>");
                finish(330);
            } else {
                // same as 1 but may want to change later
                messageContainer.html("<span>The username or password you entered is incorrect.</span>");
                finish(330);
            }
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
            finish(310);
        });
        
        return false;
    });
    
});