/*
    Signup routine script.
*/

$(document).ready(function(){

    // same as address button
    $("#same_address").click(function(){
        if (this.checked){ // copy field values and make uneditable
            $("#id_address").val($("#id_street").val());
            $("#id_city2").val($("#id_city").val());
            $("#id_state2").val($("#id_state").val());
            $("#id_zip2").val($("#id_zip").val());
            
            $("#id_address").attr("disabled", true);
            $("#id_city2").attr("disabled", true);
            $("#id_state2").attr("disabled", true);
            $("#id_zip2").attr("disabled", true);
        } else { // make editable
            $("#id_address").attr("disabled", false);
            $("#id_city2").attr("disabled", false);
            $("#id_state2").attr("disabled", false);
            $("#id_zip2").attr("disabled", false);
        }
    });

    // prepare the dialog
    var dl_signup = $( "#dialog-signup" );
    dl_signup.dialog({ autoOpen: false, modal: true, 
        beforeClose: function(event, ui) { return false; }, 
        title: "Signing Up",
        resizable: false,
        minWidth: 330, maxWidth: 330, 
        minHeight: 120, maxHeight: 120,
    });
    
    // for associated account routine
    var associatedAccountAttempts = 0;

    var messageContainer = $("#dialog-signup-message");
    $("#signup-form-submit").click(function(){
        // make sure that this has default message
        messageContainer.html("Processing your information.<br/>Please wait.");
        // update the phone number's value
        $("#id_phone_number").val(new String($("#Ph1").val()) + 
            new String($("#Ph2").val()) + new String($("#Ph3").val()));
            
        // open the dialog with the loading message
        dl_signup.dialog( "open" );
        // make sure the time icon is hidden
        $("#signing-up-time").hide();
        
        // make the ajax call
        var url = $("#signup-form input[name=action]").val();
        var url_redirect = $("#signup-form input[name=redirect-url]").val();
        var url_home = $("#signup-form input[name=home-url]").val();
        
        // need to enable again to serialize
        $("#id_address").attr("disabled", false);
        $("#id_city2").attr("disabled", false);
        $("#id_state2").attr("disabled", false);
        $("#id_zip2").attr("disabled", false);
        // format the cats first
        var cats = '';
        $(".closable-box").each(function(){
            cats = cats + $(this).text() + '|';
        });
        $( "#categories" ).val(cats);
        var data = $("#signup-form").serialize();
        
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
                        minHeight: 270, maxHeight: 270,
                        minWidth: 410, maxWidth: 410, 
                        beforeClose: function(event, ui) { return true; }, 
                        close: function(){
                            return;
                        }
                    });
                    // adjust the width and height + title
                    dl_signup.dialog( "option", "title", "Associated Account Detected");
                    dl_signup.dialog( "option", "width", 410 );
                    dl_signup.dialog( "option", "height", 270 );
                    
                    
                    messageContainer.css({ width: "370px"});
                    messageContainer.html($("#associated-account-div").clone().html());
                    
                    // remove the PLACEHOLDER from the id;
                    
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
                                if (aaf_res.code == 0) { // success
                                    // set the nonce and account_id and resubmit the signup form
                                    $("#signup-form input[name=aaf-nonce]").val(res.associated_account_nonce);
                                    $("#signup-form input[name=aaf-account_id]").val(res.associated_account);
                                    
                                    // prepare the dialog
                                    messageContainer.css({ width: "220px"});
                                    dl_signup.dialog({
                                        beforeClose: function(event, ui) { return false; }, 
                                        title: "Signing Up",
                                        minWidth: 330, maxWidth: 330, width: 330,
                                        minHeight: 120, maxHeight: 120,
                                    });
                                    // adjust the width and height + title
                                    dl_signup.dialog( "option", "title", "Signing Up");
                                    dl_signup.dialog( "option", "width", 330 );
                                    dl_signup.dialog( "option", "height", 120 );
    
                                    $("#signup-form-submit").click();
                                } else if (aaf_res.code == 1) { // invalid
                                    if (associatedAccountAttempts < 2) {
                                        aaf_pass.val('');
                                        aaf_pass.focus();
                                        aaf_submit.removeClass("active");
                                        aaf_message.html("Wrong password");
                                    } else {
                                        aaf_message.html("Wrong password. This was your 3rd attempt." +
                                            " You will have to start over for security purposes.");
                                        aaf_pass.hide();
                                        aaf_submit.val("Okay");
                                        aaf_submit.click(function() {
                                            window.location.replace(url_home);
                                            return false;
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
                                    
                                    
                } else if (res.code == 2){ // subscription not active. Tell them.
                    $( "#dialog-signup" ).dialog({ 
                        title: "Sign Up Complete", 
                        minHeight: 110, maxHeight: 110,
                        beforeClose: function(event, ui) { return true; }, 
                        close: function(){
                            window.location.replace(url_home);
                        }
                    });
                    // adjust the height + title
                    dl_signup.dialog( "option", "title", "Sign Up Complete");
                    dl_signup.dialog( "option", "height", 110 );
                    
                    $("#signing-up-time").show();
                    messageContainer.css("width", "250px");
                    messageContainer.html("<span style='color:#DF7401;position:relative;top:-4px;left:14px'>"+
                        "Your account is not yet active.<br/>We will get in touch with you soon.</span>");
                        
                } else if (res.code == 3){ // active subscription. redirect to dashboard.
                    messageContainer.html("<span style='color:green;'>Success! Welcome to Repunch.</span>");
                    window.location.replace(url_redirect);
                    
                }
            }
            
        };
        
        // signup!
        $.post(url, data, executeSignUp).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
        });
        
        return false;
    });
    
});
