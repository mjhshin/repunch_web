/*
    Pagination for django <---> javascript!
*/

function paginator(pagUrl, tabs, activeTab){

    /* pages start from 1 */
    function getPage(pageNum, type, order, header){
        tableHeader = $("#tab-body-" + type + " div.table-header");
        data =  {"type":type, "page":pageNum, "order":order, "header":header,};
        
        // make the ajax call
        $.get(pagUrl, data, function(res){
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
            pagContainer = $("#pag-container"), pagPage = $("#pag-page");
        var pagCountInput = $("#pag-page-" + which + "-count");
        pagCount = Math.ceil(parseFloat($("#" + which + "-count").val()) / parseFloat(pagThreshold));
        // update the current page count
        pagCountInput.val(new String(pagCount));
        
        // clear the units
        pagContainer.html("");
        // do not display the units if only 1 page
        if (pagCount == 1){ return; }
        
        // add the pag-units 
        for (var i=0; i<pagCount; i++){
            pagContainer.append("<a class='pag-unit'>" + new String(i+1) + "</a>");
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
            getPage(self.text(), type, order, header.attr("id").substring("header-".length)); 
            // remove all siblings' active class
            self.siblings().removeClass("active");
            self.addClass("active");
            // set the current page
            pagPage.val(self.text());
        });
        
    }

    // initial call
    paginate(activeTab);

    // bind the tabs
    // $("#tab-sent").click(function(){ paginate("sent"); });
    $.each(tabs, function(index, tab){
        // always goes back to page 1, first header, desc
        $("#tab-" + tab).click(function(){
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
            paginate(tab);
            getPage(1, tab, "desc", firstHeader.attr("id").substring("header-".length));
        });
    });

    // bind the headers- select all that are sortable
    $("div.table-header div.th:not(.not-sortable)").each(function(){
        var self = $(this);
        self.click(function(){
            var el = self.attr("id").substring("header-".length);
            var activeTab = $(".tab.active").attr("id").substring("tab-".length);
            var order;
            if (self.hasClass("desc")){ order = "desc"; } 
            else { order = "asc"; }
            var page = $("#pag-container a.pag-unit.active");
            if (page.length > 0){
                getPage(parseInt(page.text()), activeTab, order, el);
            } else {
                getPage(1, activeTab, order, el);
            }
        });
    });

}
