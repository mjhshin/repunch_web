/**
    Store edit js re-written.
*/

function hoursPreview(){
    return;
    // TODO format the data

    $.ajax({
        url: $("#hours_preview_url").val(),
        data: data,
        type: "POST",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            $("#store-hours-preview").html(res);
        },
        
    });

}

/**
    rowId is -x- in hours-x-row
*/
function bindDaysClick(rowId) {
    if (rowId == null) {
        rowId = "";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    $(".hours-form ul"+rowId+" .days div").click(function() {
        var self = $(this);
        if (self.hasClass("active")) {
            self.removeClass("active");
        } else {
            self.addClass("active");
        }
        
        // hours changed so update the preview
        hoursPreview();
    });
}

/**
    rowId is -x- in hours-x-row
*/
function bindRemoveRow(rowId){
    if (rowId == null) {
        rowId = "";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    
    $(".hours-form ul"+rowId+" .buttons .remove").click(function() {
        // do not remove the last row
        if ($(".hours-form > ul").length > 1) {
            $(this).closest("ul").remove();
            
        } else { // just deactivate all days
            $(this).closest("ul").children(".days").children().removeClass("active");
        }
        
        // hours may have changed so update the preview
        hoursPreview();
        
    });
    
}

function addHoursRow() {
    var orig = $(".hours-form ul:last");
    var origId = orig.attr("id").substring(5, 8);
    var copyId = "-"+String(Number(origId.substring(1,2)) + 1)+"-";
    // replace the -0- in hours-0-row with copyId
    // also remove all active classes on days
    orig.after( 
        "<ul id='hours"+copyId+"row'>"+
        orig.html().replace(new RegExp(origId, 'g'), copyId).replace(/active/g, "")+
        "</ul>"
    );
    // bind events
    bindDaysClick(copyId);
    bindRemoveRow(copyId);
}

function submitForm(){
    // TODO
}

$(document).ready(function(){

    // clicks on days
    bindDaysClick();
    
    // clicks on remove hours
    bindRemoveRow();
    
    // clicks on add hours
    $(".hours-form .add").click(function() {
        addHoursRow();
    });
    
    // clicks on submit
    var loader = $("#store-save-loading");
    $("#save-button").click(function() {
        if (!loader.is(":visible")) {
            loader.show();
            submitForm();
        }
    });
    
    // clicks on cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
    });
    

});
