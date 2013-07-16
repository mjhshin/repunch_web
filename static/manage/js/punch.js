/*
    Script for a punch event.
*/
function punchit(url){

    // only proceed if not processing a punch
    if ($("#punch-loading").css("display") != "none"){
        return;
    }

    // force remove previous notifications
    $("div.notification.hide").remove();
    
    var pc = $("#punch_code");
    var pa = $("#punch_amount");
    var mp = new Number($("#max_punches").val());
    var cont = true;
    
    // validate inputs
    if (!pc.val().length>0){
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Please enter the customer's punch code.<span></div></div>");
        cont = false;
    } else if (!pa.val().length>0){
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Please enter the amount of punches to give.<span></div></div>");
        cont = false;
    } else if (!(new Number(pa.val())>0)){
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Amount of punches must be greater than 0.<span></div></div>");
        cont = false;
    } else if ((new Number(pa.val())>mp)){
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>" +
            "<div><span><Maximum amount of punches is "+
            new String(mp) + ".<span></div></div>");
        cont = false;
    } 
    
    if (!cont){
        // make sure that the divs are being hidden
        setTimeout(function(){
                  $("div.notification.hide").animate({ height: 'toggle', opacity: 'toggle' }, 2500, function () {
                  $("div.notification.hide").remove();
                  });
                }, 2500);   
        return;
    }
    
    var data = {
        "punch_code":pc.val(),
        "num_punches":pa.val(),
        "csrfmiddlewaretoken":$("#punch-form input[name=csrfmiddlewaretoken]").val(),
    };
    
    // set indicator to loading state (sets display to block)
    $("#punch-loading").show();
    
    function finishPunching(){
        // make sure that the divs are being hidden
        setTimeout(function(){
                  $("div.notification.hide").animate({ height: 'toggle', opacity: 'toggle' }, 2500, function () {
                  $("div.notification.hide").remove();
                  });
                }, 2500);
                
        // set button to ready state (sets display to none)
        $("#punch-loading").hide();
        // clear the punch code and amount
        pc.val('');
        pa.val('');
    }
    
    // make the ajax call
    $.ajax({
        url: url,
        data: data,
        type: "POST",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            // res may be error : {u'code': 141, u'error': u'error'}
            // alert(res.code + res.error);
            if (res.hasOwnProperty("error")){
                $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
                "<div><span>Failed to punch customer.<span></div></div>");
            } else {
                $("#punch-form").append("<div id='punch-notification' class='notification success hide'>"+
                    "<div><span>Successfully gave " + pa.val() + " punches to " + res.patron_name + ".<span></div></div>");
            }
            finishPunching();
        },
        error: function(){ 
            $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
                "<div><span>Failed to punch customer.<span></div></div>");
            finishPunching();
        }
    });
    
}
