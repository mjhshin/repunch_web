/**
    Store edit js re-written.
    
*/

var allDayText = "24 hours";
var defaultCloseTime = "1700";

/**
    Returns the hours in the example format.
    {
        hours-1-day_1: "0600,1730,0",
        ...
    }
    
    The above example states that Sunday has an opening time of 6 am and closing time of 5.30 pm.
    
    The third bit represents the state of the 24 hour checkbox. 0 for unchecked, 1 for checked.
    This is used for validation - to differentiate b/w checking the checkbox for 24 hours 
    and manually entering the same open and close time.
*/
function getHoursData() {
    var data = {};
    
    $(".hours-form ul.hours-row").each(function() {
        var self = $(this);
        var openTime = self.find(".time.open select").val();
        var closeTime = self.find(".time.close select").val();
        var is24Hours = self.find(".buttons input[type='checkbox']").first()[0].checked;
        // closeTime is the same as openTime if the allday checkbox is checked.
        if (is24Hours) {
            closeTime = openTime;
        }
    
        // add all the active days
        self.find(".days .active").each(function() {
            data[$(this).attr("id")] = openTime+","+closeTime+","+(is24Hours?"1":"0");
        });
    });
    
    return data;
}

/**
    This not only shows a textual preview but also handles hours validation response
    from the server - enabling and disabling the submit button.
*/
function hoursPreview(){
    $.ajax({
        url: $("#hours_preview_url").val(),
        data: getHoursData(),
        type: "POST",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            if (res.result == "success") {
                $("#store-hours-preview").html(res.html);
                $("#hours_e > ul.errorlist > li").text("");
                $("#save-button").removeClass("gray").addClass("blue");
                
            } else {
                $("#hours_e > ul.errorlist > li").text(res.html);
                $("#save-button").removeClass("blue").addClass("gray");
                
            }
        
        },
        
    });

}

/**
    rowId is -x- in hours-x-row
*/
function bindOptionsClick(rowId) {
    if (rowId == null) {
        rowId = ".hours-row";
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
        rowId = ".hours-row";
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
        rowId = ".hours-row";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    
    $(".hours-form ul"+rowId+" .buttons .remove").click(function() {
        // do not remove the last row
        if ($(".hours-form > ul.hours-row").length > 1) {
            $(this).closest("ul.hours-row").remove();
            
        } else { // just deactivate all days
            $(this).closest("ul.hours-row").find(".days div").removeClass("active");
        }
        
        // hours may have changed so update the preview
        hoursPreview();
        
    });
    
}

/**
    Same code as rphours_util.py
    
    Returns the text of the option given the value.
    e.g. option_text("0630") returns 6:30 AM.
*/
function getReadableDay(value){
    if (value == "0000") {
        return "12 AM (Midnight)";
        
    } else if (value == "1200") {
        return "12 PM (Noon)";
        
    } else {
        var hour = Number(value.substring(0, 2));
        var ampm = "";
        if (hour >= 12) {
            if (hour > 12) {
                hour -= 12;
            }
            ampm = "PM";
        } else {
            if (hour == 0) {
                hour = 12;
            }
            ampm = "AM";
        }
            
        return String(hour)+":"+value.substring(2,4)+" "+ampm;
    }
    
}

/**
    rowId is -x- in hours-x-row
*/
function bindAllDay(rowId){
    if (rowId == null) {
        rowId = ".hours-row";
    } else {
        rowId = "#hours"+rowId+"row";
    }
    
    $(".hours-form ul"+rowId+" .buttons input[type='checkbox']").click(function() {
        // disable the close time for this row
        var self = $(this);
        var closeSelect = self.closest("ul.hours-row").find("li.time.close > select").first();
        closeSelect.attr("disabled", self[0].checked);
        
        var selectedOption = closeSelect.find("option:selected").first();     
        if (self[0].checked) {
            // set selected option text to 24 hours
            selectedOption.text(allDayText);
        } else {
            // unchecking reverts the option text
            selectedOption.text(getReadableDay(selectedOption.val()));
        }
        
        // hours may have changed so update the preview
        hoursPreview();
        
    });
    
}

function addHoursRow() {
    var lastHours = $(".hours-form ul.hours-row:last");
    var orig = $("#hours-clone");
    var origId = lastHours.attr("id");
    origId = origId.substring(origId.indexOf("-")+1, origId.lastIndexOf("-"));
    var copyId = "-"+String(Number(origId) + 1)+"-";
    // replace the -0- in hours-0-row with copyId
    // also remove all active classes on days
    lastHours.after( 
        "<ul id='hours"+copyId+"row' class='hours-row'>"+
        orig.html().replace(new RegExp("-x-", 'g'), copyId).replace(/active|checked/g, "")+
        "</ul>"
    );
    bindDaysClick(copyId);
    bindRemoveRow(copyId);
    bindOptionsClick(copyId);
    bindAllDay(copyId);
}

function submitForm(submitButton){
    if (submitButton.hasClass("gray")) {
        return;
    }

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
        submitForm($(this));
    });
    
    var loader = $("#store-save-loading");
    // clicks on cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
    });
    
    // if close time and open time are equal, set the close time to 5pm, disable it, 
    // and changed the option text to 24 hours
    $(".hours-form ul.hours-row .buttons input[type='checkbox']:checked").each(function() {
        var closeSelect = $(this).closest("ul.hours-row").find("li.time.close > select").first();
        closeSelect.val(defaultCloseTime);
        closeSelect.attr("disabled", true);
        
        var selectedOption = closeSelect.find("option:selected").first();     
        selectedOption.text(allDayText);
    });
    
    // initial preview
    hoursPreview();

});
