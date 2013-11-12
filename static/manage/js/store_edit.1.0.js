/**
    Store edit js re-written.
    
    // TODO validate hours ad they are clicking and don't show in preview if invalid
*/

/**
    Returns the hours in the example format.
    {
        hours-1-day_1: "0600,1730",
        ...
    }
    
    The above example states that Sunday has an opening time of 6 am and closing time of 5.30 pm.
*/
function getHoursData() {
    var data = {};
    
    $(".hours-form ul").each(function() {
        var self = $(this);
        var openTime = self.find(".time.open select").val();
        var closeTime = self.find(".time.close select").val();
        // closeTime is the same as openTime if the allday checkbox is checked.
        if (self.find(".buttons input[type='checkbox']").first()[0].checked) {
            closeTime = openTime;
        }
    
        // add all the active days
        self.find(".days .active").each(function() {
            data[$(this).attr("id")] = openTime+","+closeTime;
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

/**
    rowId is -x- in hours-x-row
*/
function bindAllDay(rowId){
    if (rowId == null) {
        rowId = "";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    
    $(".hours-form ul"+rowId+" .buttons input[type='checkbox']").click(function() {
        // disable the close time for this row
        var self = $(this);
        var closeSelect = self.closest("ul").find("li.time.close > select").first();
        closeSelect.attr("disabled", self[0].checked);
        
        // unchecking sets the close time to 5 apm
        if (!self[0].checked) {
            closeSelect.val("1700");
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
        orig.html().replace(new RegExp(origId, 'g'), copyId).replace(/active|checked/g, "")+
        "</ul>"
    );
    // bind events
    bindDaysClick(copyId);
    bindRemoveRow(copyId);
    bindOptionsClick(copyId);
    bindAllDay(copyId);
}

function submitForm(){
    var loader = $("#store-save-loading");
    if (loader.is(":visible")) { return; }
    loader.show();
    
    // update the phone number's value
    $("#id_phone_number").val(new String($("#Ph1").val()) + 
        new String($("#Ph2").val()) + new String($("#Ph3").val()));	   
                    
    var form = $("#account-edit-form");
    var data = form.serializeArray();
    data.push({
        name: "hours",
        value: JSON.stringify(getHoursData()),
    });
    
    $.ajax({
        url: form.attr("action"),
        data: $.param(data),
        type: "POST",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            loader.hide();
            
            if (res.result == "success") {
                window.location.replace(res.url);
            
            } else if (res.result == "error" ) {
                var newDoc = document.open("text/html", "replace");
                newDoc.write(res.html);
                newDoc.close();
            }

        },
        
    });
    
}


$(document).ready(function(){

    // clicks on days
    bindDaysClick();
    
    // clicks on remove hours
    bindRemoveRow();
    
    // clicks on allday checkbox
    bindAllDay();
    
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
    
    // make sure that if close time and open time are equal, the 
    // the selected close time is 5pm and disabled
    $(".hours-form ul .buttons input[type='checkbox']:checked").each(function() {
        // disable the close time for this row
        var self = $(this);
        var closeSelect = self.closest("ul").find("li.time.close > select").first();
        closeSelect.attr("disabled", self[0].checked);
        closeSelect.val("1700");
        
    });
    
    // initial preview
    hoursPreview();

});
