$(document).ready(function(){
/////////////////////////////////
    
var pagUrl = $("#get-page-url").val();

function getPage(pageNum){
    // detect which tab is active
    var type;
    if ($("#tab-sent").hasClass("active")){
        type = "sent";
    } else {
        type = "feedback";
    }
    
    tableHeader = $("#tab-body-" + type + " div.table-header");
    // make the ajax call
    $.get(pagUrl, {"type":type, "page":pageNum}, function(res){
        // remove the rows of the table first
        tableHeader.siblings().remove();
        // now add the result
        tableHeader.after(res);
    });
    
}
    
/*
    Called initially right after loading page and when tabs are clicked.
*/
function paginate(which){
    var pagCount, pagThreshold = $("#pag-threshold").val(),
        pagContainer = $("#pag-container");
        
    if (which == null){
        // first detect which tab is active and get the number of pages
        if ($("#tab-sent").hasClass("active")){
            pagCount = Math.ceil(parseFloat($("#sent-count").val()) / parseFloat(pagThreshold));
        } else {
            pagCount = Math.ceil(parseFloat($("#feedback-count").val()) / parseFloat(pagThreshold));
        }
    } else {
        pagCount = Math.ceil(parseFloat($(which).val()) / parseFloat(pagThreshold));
    }
    
    // do not display the units if only 1 page
    if (pagCount == 1){ return; }
    
    // add the pag-units (clear first)
    pagContainer.html("");
    for (var i=0; i<pagCount; i++){
        pagContainer.append("<a class='pag-unit'>" + new String(i+1) + "</a>");
    } 
    // activate the first pag unit
    $("#pag-container a.pag-unit:first-child").addClass("active");
    // now bind the units
    $("#pag-container a.pag-unit").click(function(){
        var self = $(this);
        getPage(self.text());
        // remove all siblings' active class
        self.siblings().removeClass("active");
        self.addClass("active");
    });
    
}

// initial call
paginate();

// bind the tabs
$("#tab-sent").click(function(){ paginate("#sent-count"); });
$("#tab-feedback").click(function(){ paginate("#feedback-count"); });

   
/////////////////////////////// 
});
