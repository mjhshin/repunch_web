/*
    Pagination for django <---> javascript!
*/

function paginator(pagUrl, tabs, activeTab){

    /* pages start from 1 */
    function getPage(pageNum, type, header, order){
        tableHeader = $("#tab-body-" + type + " div.table-header");
        data =  {"type":type, "page":pageNum};
        if (header != null){
            data["header"] = header;
            data["order"] = order;
        }
        
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
            pagContainer = $("#pag-container");
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
        // activate the first pag unit
        $("#pag-container a.pag-unit:first-child").addClass("active");
        // now bind the units
        $("#pag-container a.pag-unit").click(function(){
            var self = $(this);
            // the active tab
            var type = $(".white-box.table.tab-body.active").attr("id").substring("tab-body-".length);
            getPage(self.text(), type);
            // remove all siblings' active class
            self.siblings().removeClass("active");
            self.addClass("active");
        });
        
    }

    // initial call
    paginate(activeTab);

    // bind the tabs
    // $("#tab-sent").click(function(){ paginate("sent"); });
    $.each(tabs, function(index, tab){
        // always goes back to page 1, first header, desc
        $("#tab-" + tab).click(function(){
            paginate(tab);
            getPage(1, tab, $("#tab-body-" + tab +
            " div.table-header div.th:not(.not-sortable)").first().attr("id").substring("header-".length), "desc");
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
                getPage(parseInt(page.text()), activeTab, el, order);
            } else {
                getPage(1, activeTab, el, order);
            }
        });
    });

}
