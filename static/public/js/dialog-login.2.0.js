/*
    Script for everythin in the dialog-logjn box.
*/

$(document).ready(function(){

    var origTop;
    var recaptchaDisplayed = $("#dialog-login-form input[name=recaptcha_repunch]").length > 0;

    var dl = $( "#dialog-login" );
     // prep the login dialog
	dl.dialog({ autoOpen: false, modal: true, 
	    title: "Business Sign In", });
        
    if (recaptchaDisplayed) {
        $("#display_recaptcha").show();
        dl.dialog({minWidth: 380, minHeight: 440, maxWidth: 380, maxHeight: 440,});
	    dl.dialog("option", "height", 440);
	    dl.dialog("option", "width", 380);
    } else {
        dl.dialog({minWidth: 330, minHeight: 320, maxWidth: 330, maxHeight: 320,});
	    dl.dialog("option", "height", 320);
	    dl.dialog("option", "width", 330);
    }
    
     // prep the login dialog
	dl.dialog({ position: { at: "top" },
        open: function(event, ui) {
            var self = $(this);
            var container = $(window);
            if (recaptchaDisplayed) {
                origTop = (container.height()/2.0)-(self.outerHeight()/1.7);
            } else {
                origTop = (container.height()/2.0)-(self.outerHeight()/1.3);
            }
            self.dialog("widget").animate({top: origTop, opacity:1.0}, {duration: 300});
        },
        beforeClose: function(event, ui) {
            var self = $(this);
            var container = $(window);
            self.dialog("widget").animate({top: -1*self.outerHeight(), opacity:0}, {duration: 300});
        },
        }).dialog("widget").css({opacity:0});
	    
	$( "#header-signin-btn" ).click(function() {
		$( "#dialog-login" ).dialog( "open" );
		$("#login_username").focus();
		return false;
	});
	
    var fpdiv = $("#forgot-pass-form-div");
    var messageContainer = $("#dialog-login-message");
	
    var username = $("#login_username");
    var password = $("#login_password");
	
	// initialize the signin button
	var signInButton = $("#dialog-login-form input[type=submit]");
    signInButton.attr("disabled", "disabled");
    signInButton.removeClass("active").addClass("disabled");
        
    function finish(dim){
        if (recaptchaDisplayed) {
            dim = dim + 150;
        }
    
        if (fpdiv.css("display") != "none"){
            dl.dialog( "option", "height", dim + 20 );
        } else {
            dl.dialog( "option", "height", dim );
        }
        // need to make sure that dialog stays at the same position
        dl.dialog("widget").css({top: origTop});
    }
    
    function validateInputs(event) {
        if (recaptchaDisplayed) {
            if ($("input[name=recaptcha_response_field]").val().length == 0) {
	            signInButton.attr("disabled", "disabled");
	            signInButton.removeClass("active").addClass("disabled");
                return false;
            }
        }
        
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
	$("#login_username, #login_password").on("input propertychange", {submit:false}, validateInputs);
    if (recaptchaDisplayed) {
        $("input[name=recaptcha_response_field]").on("input propertychange", {submit:false}, validateInputs);
    }
	
    // PASSWORD RESET
    $("#forgot-pass-form a").click(function(){
        if (fpdiv.css("display") != "none"){
            return;
        }
        // adjust the height
        if (recaptchaDisplayed) {
            dl.dialog( "option", "height", 480 );
        } else {
            dl.dialog( "option", "height", 360 );
        }
        // need to make sure that dialog stays at the same position
        dl.dialog("widget").css({top: origTop});
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
    
    
    function displayRecaptcha(){
        dl.dialog({minWidth: 380, minHeight: 440, maxWidth: 380, maxHeight: 440,});
        dl.dialog("option", "height", 440);
        dl.dialog("option", "width", 380);
        // for dedicated login page
        $("div#main-content").css({ "min-height": "360px", "height": "360px"});
        $("input[name=recaptcha_response_field]").val("").on("input propertychange", {submit:false}, validateInputs);
        
        recaptchaDisplayed = true;
        $("#display_recaptcha").show();
    }
    
    function executeSignIn() {
        var loading = $("#logging-in");
        // prevent multiple button clicks
        if (loading.css("display") != "none"){
            return false;
        }
        // show the loading indicator
        dl.dialog( "option", "height", dl.dialog( "option", "height") + 14 );
        // need to make sure that dialog stays at the same position
        dl.dialog("widget").css({top: origTop});
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
                var dim = 324;
                if ($("#dialog-login-message span[name=incorrect]").length > 0){
                    dim += 20;
                }
                finish(dim);
            } else if (res.code == 2){
                messageContainer.html("<span>Your account is not active.</span>");
                $("#login_password").removeClass("input-text-error");
                loading.hide();
                finish(324);
            } else if (res.code == 1){
                if (res.display_recaptcha) {
                    displayRecaptcha();
                }
                messageContainer.html("<span name='incorrect'>Incorrect email or password.</span>");
                var pass = $("#login_password");
                pass.addClass("input-text-error");
                pass.val('');
                pass.focus();
                loading.hide();
                finish(324);
            } else if (res.code == 4){
                messageContainer.html("<span name='incorrect'>You do not have permission to access the dashboard.</span>");
                $("#login_password").removeClass("input-text-error");
                loading.hide();
                finish(344);
            } else if (res.code == 5){
                messageContainer.html("<span name='incorrect'>You are not yet approved.</span>");
                $("#login_password").removeClass("input-text-error");
                loading.hide();
                finish(324);
            } else {
                // same as 1 but may want to change later
                //messageContainer.html("<span name='incorrect'>The username or password you entered is incorrect.</span>");
                messageContainer.html("<span name='incorrect'>Incorrect email or password.</span>");
                var pass = $("#login_password");
                pass.addClass("input-text-error");
                pass.val('');
                pass.focus();
                loading.hide();
                finish(324);
            }
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span name='incorrect'>Error. Please try again.</span>");
            $("#login_password").removeClass("input-text-error");
            loading.hide();
            finish(324);
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
