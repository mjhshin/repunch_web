/*
    Script for everythin in the dialog-logjn box.
*/

$(document).ready(function(){

    // prep the login dialog
	$( "#dialog-login" ).dialog({ autoOpen: false, modal: true, 
	    title: "Business Sign In",
	    show: {
            effect: "slide",
            duration: 300
        },
	    hide: {
            effect: "slide",
            duration: 300
        },
	    minWidth: 330, minHeight: 316,
	    maxWidth: 330, maxHeight: 350,
	    height: 310, width: 330 });
	    
	$( "#header-signin-btn" ).click(function() {
		$( "#dialog-login" ).dialog( "open" );
		$("#id_username").focus();
		return false;
	});
	
	
    var dl = $( "#dialog-login" );
    var loadingHeight = 10;
    var fpdiv = $("#forgot-pass-form-div");
    var messageContainer = $("#dialog-login-message");
	
    var username = $("#id_username");
    var password = $("#id_password");
	
	// initialize the signin button
	var signInButton = $("#dialog-login-form input[type=submit]");
    signInButton.attr("disabled", "disabled");
    signInButton.removeClass("active").addClass("disabled");
        
    function finish(dim){
        if (fpdiv.css("display") != "none"){
            dl.dialog( "option", "height", dim + 50 );
        } else {
            dl.dialog( "option", "height", dim );
        }
    }
    
    function validateInputs(event) {
        var submit = event.data.submit;
	    var unLength = $.trim(username.val()).length;
	    var pwLength = $.trim(password.val()).length;
	    if (unLength == 0 && pwLength == 0) {
	        signInButton.attr("disabled", "disabled");
	        signInButton.removeClass("active").addClass("disabled");
	        if (submit) {
	            finish(320);
                messageContainer.html("<span name='incorrect'>Enter your email and password.</span>");
                return false;
            }
	    } else if (unLength == 0 && pwLength > 0) {
	        signInButton.attr("disabled", "disabled");
	        signInButton.removeClass("active").addClass("disabled");
	        if (submit) {
	            finish(320);
                messageContainer.html("<span name='incorrect'>Please enter your email.</span>");
                return false;
            }
	    } else if (unLength > 0 && pwLength == 0) {
	        signInButton.attr("disabled", "disabled");
	        signInButton.removeClass("active").addClass("disabled");
	        if (submit) {
	            finish(320);
                messageContainer.html("<span name='incorrect'>Please enter your password.</span>");
                return false;
            }
	    } else {
	        signInButton.removeAttr("disabled");
	        signInButton.removeClass("disabled").addClass("active");
	        if (submit) {
	            return true;
	        }
	    }
	    
	}
	
	// add the listeners to username and password fields
	$("#id_username, #id_password").keyup({submit:false}, validateInputs);
	
    // PASSWORD RESET
    $("#forgot-pass-form a").click(function(){
        if (fpdiv.css("display") != "none"){
            return;
        }
        // adjust the height
        dl.dialog( "option", "height", 360 );
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
    
    function executeSignIn() {
        var loading = $("#logging-in");
        // prevent multiple button clicks
        if (loading.css("display") != "none"){
            return false;
        }
        // show the loading indicator
        dl.dialog( "option", "height", dl.dialog( "option", "height") + loadingHeight );
        loading.show();
        
        var url = $("#dialog-login input[name=action]").val();
        var data = $("#dialog-login-form").serialize();
        
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
                window.location.replace(res.redirect_url);
                var dim = 320;
                if ($("#dialog-login-message span[name=incorrect]").length > 0){
                    dim += 20;
                }
                finish(dim);
            } else if (res.code == 2){
                messageContainer.html("<span>Your account is not active.</span>");
                $("#id_password").removeClass("input-text-error");
                loading.hide();
                finish(320);
            } else if (res.code == 1){
                //messageContainer.html("<span name='incorrect'>The username or password you entered is incorrect.</span>");
                messageContainer.html("<span name='incorrect'>Incorrect email or password.</span>");
                var pass = $("#id_password");
                pass.addClass("input-text-error");
                pass.val('');
                pass.focus();
                loading.hide();
                finish(320);
            } else if (res.code == 4){
                messageContainer.html("<span name='incorrect'>You do not have permission to access the dashboard.</span>");
                $("#id_password").removeClass("input-text-error");
                loading.hide();
                finish(340);
            } else if (res.code == 5){
                messageContainer.html("<span name='incorrect'>You are not yet approved.</span>");
                $("#id_password").removeClass("input-text-error");
                loading.hide();
                finish(320);
            } else {
                // same as 1 but may want to change later
                //messageContainer.html("<span name='incorrect'>The username or password you entered is incorrect.</span>");
                messageContainer.html("<span name='incorrect'>Incorrect email or password.</span>");
                var pass = $("#id_password");
                pass.addClass("input-text-error");
                pass.val('');
                pass.focus();
                loading.hide();
                finish(320);
            }
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span name='incorrect'>Error. Please try again.</span>");
            $("#id_password").removeClass("input-text-error");
            loading.hide();
            finish(320);
        });
        
        return false;
    }
    
    var submitEvent = {data:{submit:true}};
    
    // LOGIN
    signInButton.click(function(){
        if (!validateInputs(submitEvent)) {
            return false;
        }
        return executeSignIn();
    });
    
    // handle the enter key
	$("#dialog-login-form").keypress(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            
            if (!validateInputs(submitEvent)) {
                return false;
            }
            return executeSignIn();
        }
    });
    
});
