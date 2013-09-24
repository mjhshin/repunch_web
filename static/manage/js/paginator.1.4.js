/*
    Pagination for django <---> javascript!
*/

var paginate, getPage, onHeaderClick, onTabClick;
var MAX_PAG_UNIT_COUNT = 11;

/*
    getCallback is called after every successful ajax call to the
    server to fetch the sorted chunk of rows.
*/
function paginator(pagUrl, tabs, activeTab, getCallback){
    // initial call
    paginate(pagUrl, activeTab, getCallback);

    // rebind the tabs
    // $("#tab-sent").click(function(){ paginate("sent"); });
    $.each(tabs, function(index, tab){
        // always goes back to page 1, first header, desc
        $("#tab-" + tab).unbind("click", onTabClick);
        $("#tab-" + tab).bind("click", {"tab":tab, "pagUrl":pagUrl, "getCallback":getCallback}, onTabClick);
    });

    // rebind the headers- select all that are sortable
    $("div.table-header div.th:not(.not-sortable)").each(function(){
        var self = $(this);
        self.unbind("click",onHeaderClick);
        self.bind("click", {"self":self, "pagUrl":pagUrl, "getCallback":getCallback}, onHeaderClick);
    });

}

/* pages start from 1 */
getPage = function (pagUrl, pageNum, type, order, header, getCallback){
    tableHeader = $("#tab-body-" + type + " div.table-header");
    data =  {"type":type, "page":pageNum, "order":order, "header":header,};
    
    $.ajax({
        url: pagUrl,
        data: data,
        type: "GET",
        cache:false, // required to kill internet explorer 304 bug
        success: function(res){
            // remove the rows of the table first
            tableHeader.siblings().remove();
            // now add the result
            tableHeader.after(res);
            // call the getCallback if provided
             if (getCallback != null){
                getCallback();
            }
        }
    });
    
}

/*
    Called initially right after loading page and when tabs are clicked.
*/
paginate = function (pagUrl, which, getCallback) {
    var pagThreshold = $("#pag-threshold").val(),
        pagContainer = $("#pag-container"), pagPage = $("#pag-page");
    var pagCountInput = $("#pag-page-" + which + "-count");
    var pagCount = Math.ceil(parseFloat($("#" + which + "-count").val()) / parseFloat(pagThreshold));
    // update the current page count
    pagCountInput.val(new String(pagCount));
    
    // clear the units
    pagContainer.html("");
    // do not display the units if only 1 page
    if (pagCount == 1){ return; }
    
    // add the pag-units 
    if (pagCount > MAX_PAG_UNIT_COUNT) {
        var pagePageNum = new Number(pagPage.val());
        // show up to 4 to the left and 4 to the right
        var numLeft = pagePageNum - parseInt(MAX_PAG_UNIT_COUNT/2);
        if (numLeft <= 0) { numLeft = 1; }
        var numRight = pagePageNum + parseInt(MAX_PAG_UNIT_COUNT/2);
        if (numRight > pagCount) { numRight = pagCount; }
        
        var diff = numRight - numLeft;
        if (diff < MAX_PAG_UNIT_COUNT - 2) { // subtract 2 for first and last
            if (numLeft == 1) { // left side is maxed
                numRight = numRight + ((MAX_PAG_UNIT_COUNT - 2) - diff);
            } else if (numRight == pagCount){ // right is maxed
                numLeft = numLeft - ((MAX_PAG_UNIT_COUNT - 2) - diff);
            }
        }
        
        pagContainer.append("<a class='pag-unit'>first</a>");
        for (var i=numLeft; i<numRight; i++){
            pagContainer.append("<a class='pag-unit'>" + new String(i+1) + "</a>");
        }   
        pagContainer.append("<a class='pag-unit'>last</a>");
    } else {
        for (var i=0; i<pagCount; i++){
            pagContainer.append("<a class='pag-unit'>" + new String(i+1) + "</a>");
        } 
    }
    // activate the current page pag unit
    $("#pag-container a.pag-unit:nth-child(" + new String(pagPage.val()) + ")").addClass("active");
    // now bind the units
    $("#pag-container a.pag-unit").click(function(){
        var self = $(this);
        // the active tab
        var type = $(".white-box.table.tab-body.active").attr("id").substring("tab-body-".length);
        // get the order from the active header (flagged by 'sorted')
        var order, header = $("#tab-body-" + which +
            " div.table-header div.th.sorted");
        if (header.hasClass("desc")) {
            order = "desc";
        } else {
            order = "asc";
        }
        
        var pageNumStr;
        if (self.text() == "first") {
            pageNumStr = "1";
        } else if(self.text() == "last") {
            pageNumStr = new String(pagCount);
        } else {
            pageNumStr = self.text();
        }
        
        getPage(pagUrl, parseInt(pageNumStr), type, order, header.attr("id").substring("header-".length), getCallback); 
        
        // renumber the units if passed the threshold;
        if (pagCount > MAX_PAG_UNIT_COUNT) {
            var pagePageNum;  
            if (self.text() == "first") {
                pagePageNum = 1;
            } else if (self.text() == "last") {
                pagePageNum = pagCount;
            } else {
                pagePageNum = new Number(self.text());
            }
            // show up to 4 to the left and 4 to the right
            var numLeft = pagePageNum - parseInt(MAX_PAG_UNIT_COUNT/2);
            var numRight = pagePageNum + parseInt(MAX_PAG_UNIT_COUNT/2);
            // truncate
            if (numLeft <= 1) { 
                numLeft = 1;
            }
            
            var diff = numRight - numLeft;
            if (diff < MAX_PAG_UNIT_COUNT - 2) { // subtract 2 for first and last
                if (numLeft <= 1) { // left side is maxed
                    numRight = numRight + ((MAX_PAG_UNIT_COUNT - 2) - diff);
                } else if (numRight >= pagCount){ // right is maxed
                    numLeft = numLeft - ((MAX_PAG_UNIT_COUNT - 2) - diff);
                }
            } else if (diff > MAX_PAG_UNIT_COUNT - 2) {
                numRight = numRight - (diff - (MAX_PAG_UNIT_COUNT - 2));
                numLeft = numLeft - (diff - (MAX_PAG_UNIT_COUNT - 2) - 1);
            } else {
                if (numRight >= pagCount){ // right is maxed
                    numLeft = numLeft - 1;
                }
            }
            // truncate again
            if (numRight >= pagCount) { 
                numRight = pagCount - 1;
                numLeft = pagCount - (MAX_PAG_UNIT_COUNT  - 2) - 1;
            }
            if (numLeft <= 1) { 
                numLeft = 1;
            }
            
            var countTmp = numLeft - 1;
            $(".pag-unit").each(function() {
                var self = $(this);
                if (countTmp == numLeft - 1) {
                    self.text("first");
                } else if (countTmp == numRight) {
                    self.text("last");
                } else {
                    self.text(new String(countTmp + 1));
                }
                if (new Number(pageNumStr) - 1 == countTmp) {
                    // remove all siblings' active class
                    self.siblings().removeClass("active");
                    self.addClass("active");
                    // set the current active unit
                    pagPage.val(countTmp);
                }
                countTmp = countTmp + 1;
            });
            
        } else {
            // remove all siblings' active class
            self.siblings().removeClass("active");
            self.addClass("active");
            // set the current active unit
            pagPage.val(pageNumStr);
        }
        
    });
    
}

onHeaderClick = function(event){
    var self = event.data.self;
    var pagUrl = event.data.pagUrl;
    var getCallback = event.data.getCallback;
    var el = self.attr("id").substring("header-".length);
    var activeTab = $(".tab.active").attr("id").substring("tab-".length);
    var order;
    if (self.hasClass("desc")){ order = "desc"; } 
    else { order = "asc"; }
    var page = $("#pag-container a.pag-unit.active");
    // if first and last pag-units are present
    var pagThreshold = $("#pag-threshold").val();
    var pagCount = Math.ceil(parseFloat($("#" + activeTab + "-count").val()) / parseFloat(pagThreshold));
    var pageNumStr;
    if (page.text() == "first") {
        pageNumStr = "1";
    } else if(page.text() == "last") {
        pageNumStr = new String(pagCount);
    } else {
        pageNumStr = page.text();
    }
    
    
    if (page.length > 0){
        getPage(pagUrl, parseInt(pageNumStr), activeTab, order, el, getCallback);
    } else {
        getPage(pagUrl, 1, activeTab, order, el, getCallback);
    }
};

onTabClick = function(event){
    var tab = event.data.tab;
    var pagUrl = event.data.pagUrl;
    var getCallback = event.data.getCallback;
    // set the page
    $("#pag-page").val("1");
    // deactivate all headers
    var headers = $("#tab-body-" + tab +
        " div.table-header div.th:not(.not-sortable)");
    headers.removeClass("sorted");
    headers.removeClass("asc");
    headers.removeClass("desc");
    // activate first header
    var firstHeader = headers.first();
    firstHeader.addClass("sorted");
    firstHeader.addClass("desc");
    // repaginate and get the first page
    paginate(pagUrl, tab, getCallback);
    getPage(pagUrl, 1, tab, "desc", firstHeader.attr("id").substring("header-".length), getCallback);
};