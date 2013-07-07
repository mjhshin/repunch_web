// for the workbench page TODO fetch items from next page?
function onRedeem(rowId){
    var urlRedeem = $("#redeem-url").val();
    var row = $("#" + rowId);
    var rewardId = $("#" + rowId + " input[type=hidden]").val();
    var customerName = $("#" + rowId + " div:nth-child(3)").text();
    var title = $("#" + rowId + " div:nth-child(4)").text();
    var numPunches = $("#" + rowId + " div:nth-child(5)").text();
    $.ajax({
        url: urlRedeem,
        data: {"redeemRewardId":rowId,
                "rewardId":rewardId }, 
        type: "GET",
        success: function(res){
            if (res.result == 1 || res.result == 2){
                if (res.result == 1){
                    row.css("background", "#CCFF99");
                    row.html("Successfully validated redemption.");
                } else {
                    row.css("background", "#ffffcb");
                    row.html("Customer does not have enough punches!");
                    alert("Customer does not have enough punches!");
                }
                row.fadeOut(2000, function(){
                    // no longer necessary to append to past redemptions since
                    // clicking on redeem means that the redemption tab is active...
                    
                    // then remove
                    $(this).remove();
                                            
                    // update the counts
                    var rBadge = $("#redemptions-nav a div.nav-item-badge");
                    var diva = $("#redemptions-nav a");
                    var rcount = new String($("#tab-body-pending-redemptions div.tr").length);
                    if (rcount < 1){
                        // workbench nav badge
                        if (rBadge.length == 1){
                            rBadge.fadeOut(1000, function(){
                                $(this).remove();
                            });
                        }
                        
                        // update the title
                        if (parseInt(rcount) > 0) {
                            document.title = "Repunch | (" + rcount + ") Redemptions";
                        } else {
                            document.title = "Repunch | Redemptions";
                        }
                        
                        // pending tab
                        $("#tab-pending-redemptions").html("Pending");
                        
                        // place the placeholder if now empty
                        $("#tab-body-pending-redemptions div.table-header").after(
                            "<div class='tr' id='no-redemptions'>" +
			                "<div class='td'>No Redemptions</div>" +
		                    "</div>");
                    } else {
                        // workbench nav badge
                        if (rBadge.length == 1){
                            rBadge.text(rcount);
                        } else {
                            diva.append("<div class='nav-item-badge'>" +
                                rcount + "</div>");
                        }
                        
                        // pending tab
                        $("#tab-pending-redemptions").html("Pending (" + rcount + ")");
                        
                    }
                    
                });
            } else {
                alert("Redemption failed");
            }
        },
        error: function(res){
            // TODO
        },
    });
}

var onRedeemRebind = function (event) {
    var self = event.data.self;
    onRedeem(self.attr("name"));
}

// specify a callback to bind the fresh html chunk received from the server
var rebindRedemptions = function (){
    // WARNING! May unbind other functions other than onRedeem
    $("#tab-body-pending-redemptions div.tr div.td a").each(function(){
        var self = $(this);
        self.unbind("click", onRedeemRebind);
        self.bind("click", {"self":self}, onRedeemRebind); 
    });
}
