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
    $( "#dialog-signup" ).dialog({ autoOpen: false, modal: true, 
        beforeClose: function(event, ui) { return false; }, 
        title: "Signing up",
        resizable: false,
        minWidth: 330, minHeight: 120,
        maxWidth: 330, maxHeight: 120, });

    var messageContainer = $("#dialog-signup-message");
    $("#signup-form-submit").click(function(){
        // make sure that this has default message
        messageContainer.html("Processing your information.<br/>Please wait.");
        // update the phone number's value
        $("#id_phone_number").val(new String($("#Ph1").val()) + 
            new String($("#Ph2").val()) + new String($("#Ph3").val()));
            
        // open the dialog with the loading message
        $( "#dialog-signup" ).dialog( "open" );
        // make sure the time icon is hidden
        $("#signing-up-time").hide();
        
        // make the ajax call
        var url = $("#signup-form input[name=action]").val();
        var url_redirect = $("#signup-form input[name=redirect-url]").val();
        var url_home = $("#signup-form input[name=home-url]").val();
        // uncomment below when credit card info is brought back on sign up
        // var url_signup2 = $("#signup-form input[name=signup2]").val();
        
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
                        title: "Sign up complete", 
                        minHeight: 110, maxHeight: 110,
                        beforeClose: function(event, ui) { return true; }, 
                        close: function(){
                            window.location.replace(url_home);
                        } });
                    $("#signing-up-time").show();
                    messageContainer.css("width", "250px");
                    messageContainer.html("<span style='color:#DF7401;position:relative;top:-4px;left:14px'>"+
                        "Your account is not yet active.<br/>We will get in touch with you soon.</span>");
                } else if (res.code == 3){ // active subscription. redirect to dashboard.
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
