
function onRedeem(rowId, action){
    var urlRedeem = $("#redeem-url").val();
    var row = $("#" + rowId);
    var rewardId = $("#" + rowId + " input[type=hidden]").val();
    var customerName = $("#" + rowId + " div:nth-child(3)").text();
    var title = $("#" + rowId + " div:nth-child(4)").text();
    var numPunches = $("#" + rowId + " div:nth-child(5)").text();
    $.ajax({
        url: urlRedeem,
        data: {"redeemRewardId":rowId,
                "rewardId":rewardId,
                "action":action }, 
        type: "GET",
        success: function(res){
            if (res.result == 1 || res.result == 2 || res.result == 3 || res.result == 4 || res.result == 5){
                if (res.result == 1){
                    row.css("background", "#CCFF99");
                    row.html("Successfully <span style='color:blue'>APPROVED</span> redemption.");
                } else if (res.result == 3){
                    row.css("background", "#FFFFCB");
                    row.html("Reward already redeemed.");
                    alert("Invalid! Reward already redeemed.");
                } else if (res.result == 4) {
                    row.css("background", "#CCFF99");
                    row.html("Successfully <span style='color:red'>DENIED</span> redemption.");
                } else if (res.result == 5) {
                    row.css("background", "#FFFFCB");
                    row.html("Redemption has been <span style='color:red'>DENIED</span> elsewhere.");
                } else {
                    row.css("background", "#FFFFCB");
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
                    var rcount = $("#tab-body-pending-redemptions div.tr").length;
                    
                    // update the title
                    if (rcount > 0) {
                        document.title = "Repunch | (" + new String(rcount) + ") Redemptions";
                    } else {
                        document.title = "Repunch | Redemptions";
                    }
                    
                    if (rcount < 1){
                        // workbench nav badge
                        if (rBadge.length == 1){
                            rBadge.fadeOut(1000, function(){
                                $(this).remove();
                            });
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
                            rBadge.text(new String(rcount));
                        } else {
                            diva.append("<div class='nav-item-badge'>" +
                                new String(rcount) + "</div>");
                        }
                        
                        // pending tab
                        $("#tab-pending-redemptions").html("Pending (" + new String(rcount) + ")");
                        
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
    var action = event.data.action;
    onRedeem(self.attr("name"), action);
}

// specify a callback to bind the fresh html chunk received from the server
var rebindRedemptions = function (){
    // Redbind approvals
    $("#tab-body-pending-redemptions div.tr div.td a:nth-child(1)").each(function(){
        var self = $(this);
        self.unbind("click", onRedeemRebind);
        self.bind("click", {"self":self, "action":"approve"}, onRedeemRebind); 
    });
    // Redbind denials
    $("#tab-body-pending-redemptions div.tr div.td a:nth-child(2)").each(function(){
        var self = $(this);
        self.unbind("click", onRedeemRebind);
        self.bind("click", {"self":self, "action":"deny"}, onRedeemRebind); 
    });
}
