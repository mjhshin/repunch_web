/*
    Signup routine script.
*/

$(document).ready(function(){

    $( "#dialog-signup" ).dialog({ autoOpen: false, modal: true, 
        title: "Signing up",
        minWidth: 330, minHeight: 100,
        maxWidth: 330, maxHeight: 100, });

    var messageContainer = $("#dialog-signup-message");
    $("#signup-form-submit").click(function(){
        // open the dialog with the loading message
        $( "#dialog-signup" ).dialog( "open" );
        // make the ajax call
        var url = $("#signup-form input[name=action]").val();
        var data = $("#signup-form").serialize();
        $.post(url, data, function(res, status, xhr) {
            respType = xhr.getResponseHeader("content-type");
            if (respType.indexOf("html") != -1){
                // form had errors, replace entire page
                var newDoc = document.open("text/html", "replace");
                newDoc.write(res);
                newDoc.close();
                $( "#dialog-signup" ).dialog( "close" );
            } else if (respType.indexOf("json") != -1){
                // success! check code
                
            }
        }).fail(function(){  // should not go here unless server error
            messageContainer.html("<span>Server Error</span>");
        });
        
        return false;
    });
    
});
