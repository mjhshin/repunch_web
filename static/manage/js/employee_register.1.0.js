$(document).ready(function(){

    // prepare the dialog
    var dl_signup = $( "#dialog-signup" );
    dl_signup.dialog({ autoOpen: false, modal: true, 
        beforeClose: function(event, ui) { return false; }, 
        title: "Registering",
        resizable: false,
        minWidth: 350, maxWidth: 350, 
        minHeight: 140, maxHeight: 140,
    });
    
    // for associated account routine
    var associatedAccountAttempts = 0;
    var messageContainer = $("#dialog-signup-message");
    
    $("#register-employee-submit").click(function(){
        // make sure that this has default message
        messageContainer.html("Processing your information.<br/>Please wait.");
            
        // open the dialog with the loading message
        dl_signup.dialog( "open" );
        // make sure the time icon is hidden and the loading is shown
        $("#signing-up-time").hide();
        $("#signing-up").show();
        
        // make the ajax call
        var url = $("#employee-register-form input[name=action]").val();
        var url_redirect = $("#employee-register-form input[name=redirect-url]").val();
        var url_home = $("#employee-register-form input[name=home-url]").val();
        var data = $("#employee-register-form").serialize();
        
        function executeSignUp(res, status, xhr) {
            $("#signing-up").hide();
            respType = xhr.getResponseHeader("content-type");
            
            if (respType.indexOf("html") != -1){
                // form had errors, replace entire page
                var newDoc = document.open("text/html", "replace");
                newDoc.write(res);
                newDoc.close();
                dl_signup.dialog( "close" );
            } else if (respType.indexOf("json") != -1){
                if (res.code == 0){ // Associated account already exists.
                    dl_signup.dialog({ 
                        title: "Associated Account Detected", 
                        minHeight: 280, maxHeight: 280,
                        minWidth: 490, maxWidth: 490, 
                        beforeClose: function(event, ui) { return true; }, 
                        close: function(){
                            window.location.replace(url_home);
                        }
                    });
                    // adjust the width and height + title
                    dl_signup.dialog( "option", "title", "Associated Account Detected");
                    dl_signup.dialog( "option", "width", 490 );
                    dl_signup.dialog( "option", "height", 280 );
                    
                    
                    messageContainer.css({ width: "420px"});
                    messageContainer.html($("#associated-account-div").clone().html());
                    
                    var aaf = $("#dialog-signup-message #associated-account-form");
                    var aaf_nonce = $("#dialog-signup-message #associated-account-form input[name=aaf-nonce]");
                    var aaf_acc_id = $("#dialog-signup-message #associated-account-form input[name=aaf-account_id]");
                    var aaf_uname = $("#dialog-signup-message #associated-account-form input[name=acc_username]");
                    var aaf_pass = $("#dialog-signup-message #associated-account-form input[name=acc_password]");
                    var aaf_submit = $("#dialog-signup-message #associated-account-form input[type=submit]");
                    
                    var aaf_url = $("#dialog-signup-message #associated-account-form input[name=url]").val();
                    var aaf_message = $("#dialog-signup-message #associated-account-message");
    
                    // set username/email and nonce + acc_id
                    aaf_uname.val(res.email);
                    aaf_nonce.val(res.associated_account_nonce);
                    aaf_acc_id.val(res.associated_account);
                    
                    aaf_pass.attr("placeholder",
                        "Enter password for " + res.email);
                    aaf_pass.focus();
                        
                    // bind events
                    aaf_pass.keyup(function() {
                        if ($(this).val().length > 0) {
                            aaf_submit.addClass("active");
                        } else {
                            aaf_submit.removeClass("active");
                        }
                    });
                    
                    function submitAAF() {
                        if (aaf_submit.hasClass("active")) {
                            var aaf_data = aaf.serialize();
                            $.post(aaf_url, aaf_data, function(aaf_res, aaf_status, aaf_xhr) {
                                if (aaf_res.code == 0) { // SUCCESS
                                    // set the nonce and account_id and resubmit the signup form
                                    $("#employee-register-form input[name=aaf-nonce]").val(res.associated_account_nonce);
                                    $("#employee-register-form input[name=aaf-account_id]").val(res.associated_account);
                                    
                                    // prepare the dialog
                                    messageContainer.css({ width: "220px"});
                                    dl_signup.dialog({
                                        beforeClose: function(event, ui) { return false; }, 
                                        title: "Registering",
                                        minWidth: 350, maxWidth: 350,
                                        minHeight: 140, maxHeight: 140,
                                    });
                                    // adjust the width and height + title
                                    dl_signup.dialog( "option", "title", "Signing Up");
                                    dl_signup.dialog( "option", "width", 350 );
                                    dl_signup.dialog( "option", "height", 140 );
    
                                    $("#register-employee-submit").click();
                                } else if (aaf_res.code == 1) { // INVALID
                                    if (associatedAccountAttempts < 2) {
                                        dl_signup.dialog({minHeight: 310, maxHeight: 310,});
                                        dl_signup.dialog( "option", "height", 310 );
                                        
                                        aaf_pass.val('');
                                        aaf_pass.focus();
                                        aaf_submit.removeClass("active");
                                        aaf_message.html("Wrong password");
                                    } else {
                                        dl_signup.on( "dialogclose", function( event, ui ) {
                                            window.location.replace(url_home);
                                        });
                                        dl_signup.dialog({minHeight: 320, maxHeight: 320,});
                                        dl_signup.dialog( "option", "height", 320 );
                                        
                                        // error message
                                        aaf_message.html("Wrong password. This was your 3rd attempt." +
                                            " You will have to start over for security purposes.");
                                        aaf_pass.hide();
                                        aaf_submit.val("OK");
                                        aaf_submit.click(function() {
                                            window.location.replace(url_home);
                                            return false;
                                        });
                                        
                                        // forgot password link
                                        var aaFPassForm = $("#aa-forgot-pass-form");
                                        var aaFPassFormSpan = $("#aa-forgot-pass-form span");
                                        var aaFPassFormLink = $("#aa-forgot-pass-form span a");
                                        aaFPassFormLink.show();
                                        aaFPassFormLink.click(function() {
                                            aaFPassFormLink.unbind("click");
                                            $("#aa-forgot-pass-form input[name=forgot-pass-email]").val(res.email);
                                            $.post($("#aa-forgot-pass-form input[name=action]").val(), 
                                                    $("#aa-forgot-pass-form").serialize(), function(aaFPRes){
                                                if (aaFPRes.res){
                                                    aaFPassFormSpan.html("<span style='font: 14px \"Cabin\", sans-serif; color:green;'>Password Reset form sent.</span>");
                                                } else { // should never go here
                                                    aaFPassFormSpan.html("<span>Email not recognized.</span>");
                                                }
                                            });
                                        });
                                        
                                    }
                                    
                                    associatedAccountAttempts += 1;
                                }
                            });
                        }
                        
                        return false;
                    };
                    
                    // prevent enter key
                    aaf.keypress(function(event) {
                        if (event.which == 13) {
                            event.preventDefault();
                            submitAAF();
                            return false;
                        }
                    });
                    
                    // submit the form
                    aaf_submit.click(submitAAF);
                                    
                                    
                } else { // success || error
                    var title, message;
                    
                    if (res.code == 2) {
                        title = "Register Complete";
                        message = "<span style='color:green;'>You are now a registered employee.<br/>Congratulations.</span>";
                    } else {
                        title = "Register Failed";
                        message = "<span style='color:#900;'>Something went wrong.<br/>Please try again.</span>";
                    }
                
                    dl_signup.dialog({ 
                        title: title, 
                        minWidth: 360, maxWidth: 360, 
                        beforeClose: function(event, ui) { return true; }, 
                        close: function(){
                            window.location.replace(url_home);
                        }
                    });
                    // adjust the height + title
                    dl_signup.dialog( "option", "title", title);
                    dl_signup.dialog( "option", "width", 360 );
                    
                    // $("#signing-up-time").show();
                    messageContainer.css("width", "250px");
                    messageContainer.html(message);
                }
            }
            
        };
        
        // register!
        $.post(url, data, executeSignUp).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
        });
        
        return false;
    });
    
});
