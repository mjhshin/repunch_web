/*
    Script for a punch event.
*/

Object.prototype.hasOwnProperty = function(property) {
    return this[property] !== undefined;
};

function punchit(url){

    // only proceed if not processing a punch
    if ($("#punch-loading").css("display") != "none"){
        return;
    }

    // force remove previous notifications
    $("div.notification.hide").remove();
    
    var pc = $("#punch_code");
    var pa = $("#punch_amount");
    var ei = $("#employee_id");
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
    } else if (!ei.val().length>0){
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Please enter the your employee ID.<span></div></div>");
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
        "employee_id":ei.val(),
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
    }
    
    // make the ajax call
    $.post(url, data, function(res) {
        // res may be error : {u'code': 141, u'error': u'error'}
        // alert(res.code + res.error);
        if (res.hasOwnProperty("error")){
            $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Failed to punch customer.<span></div></div>");
        } else {
            $("#punch-form").append("<div id='punch-notification' class='notification success hide'>"+
                "<div><span>Successfully gave " + pa.val() + " punches to " + pc.val() + ".<span></div></div>");
            
        }
        finishPunching();
    }).fail(function(){ 
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Failed to punch customer.<span></div></div>");
        finishPunching();
    });

    
    
}
