/**
    Store edit js re-written.
*/

/**
    Returns the hours in the example format.
    {
        hours-1-day_1: "0600,1730" } 
        ...
    }
    
    The above example states that Sunday has an opening time of 6 am and closing time of 5.30 pm.
*/
function getHoursData() {
    var data = {};
    
    $(".hours-form ul").each(function() {
        var self = $(this);
        var openTime = self.find(".time.open select");
        var closeTime = self.find(".time.close select");
    
        // add all the active days
        self.find(".days .active").each(function() {
            data[$(this).attr("id")] = openTime.val()+","+ closeTime.val();
        });
    });
    
    return data;
}

function hoursPreview(){
    $.ajax({
        url: $("#hours_preview_url").val(),
        data: getHoursData(),
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
function bindOptionsClick(rowId) {
    if (rowId == null) {
        rowId = "";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    $(".hours-form ul"+rowId+" li.time select").change(function() {
        // hours changed so update the preview
        hoursPreview();
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
            $(this).closest("ul").find(".days div").removeClass("active");
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
    bindOptionsClick(copyId);
}

function submitForm(){
    var loader = $("#store-save-loading");
    if (loader.is(":visible")) { return; }
    loader.show();
                    
    var form = $("#account-edit-form");
    var data = form.serialize();
    data["hours"] = getHoursData();
    $.ajax({
        url: form.attr("action"),
        data: data,
        type: "POST",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            loader.hide();
            // TODO handle response
        },
        
    });
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
    
    // clicks on options
    bindOptionsClick();
    
    // clicks on submit
    $("#save-button").click(function() {
        submitForm();
    });
    
    var loader = $("#store-save-loading");
    // clicks on cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
    });
    

});
