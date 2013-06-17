/*
    Script for a punch event.
*/

function punchit(url){
    // force remove previous notifications
    $("div.notification.hide").remove();
    
    var pc = $("#punch_code");
    var pa = $("#punch_amount");
    var ei = $("#employee_id");
    var data = {
        "punch_code":pc.val(),
        "num_punches":pa.val(),
        "employee_id":ei.val(),
        "csrfmiddlewaretoken":$("#punch-form input[name=csrfmiddlewaretoken]").val(),
    };
    // make the ajax call
    $.post(url, data, function(res) {
        // res may be error : {u'code': 141, u'error': u'error'}
        // alert(res.code + res.error);
        // make sure that the divs are being hidden
        $("#punch-form").append("<div id='punch-notification' class='notification success hide'>"+
            "<div><span>Successfully gave " + pa.val() + " punches to " + pc.val() + ".<span></div></div>");
        setTimeout(function(){
          $("div.notification.hide").animate({ height: 'toggle', opacity: 'toggle' }, 2500, function () {
          $("div.notification.hide").remove();
          });
        }, 2500);
    }).fail(function(){ 
        $("#punch-form").append("<div id='punch-notification' class='notification hide'>"+
            "<div><span>Failed to punch customer.<span></div></div>");
    });

    
       
}
