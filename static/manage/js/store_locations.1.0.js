/*
    Backend for the store locations list in store details.
*/


// the lower this number is, the faster the scroll will be
var ANIMATION_DURATION = 1000;

// The values below ust be synced with the values in store_locations.css
// need to know the height of a nav item (height + padding + border)
var NAV_ITEM_HEIGHT = 40 + 20 + 1;
// need to know the height of the active nav item (height + padding + border)
var NAV_ITEM_ACTIVE_HEIGHT = 70 + 20 + 1;
// the amount of items before the scroll arrows are shown
var NAV_ITEM_SCROLL = 8;
// height of the scroll arrows (height + padding)
var SCROLL_ARROW_HEIGHT = 10 + 20;
// height of the add button (height + padding)
var ADD_BUTTON_HEIGHT = 60 + 20;
// Total height of the add button and the arrow down when scrolling is enabled.
var NAV_SCROLL_BOTTOM_STATIC_HEIGHT = SCROLL_ARROW_HEIGHT + ADD_BUTTON_HEIGHT;

/*
    Does not include the add button.
*/
function getNavItemCount() {
    return $("#store-locations > div.nav > a[class!=add]").length;
}

/*
    One of the item is active.
*/
function getNavTotalHeight() {
    return (NAV_ITEM_HEIGHT * getNavItemCount()) - NAV_ITEM_HEIGHT + NAV_ITEM_ACTIVE_HEIGHT;
}

/*
    The Root container height.
*/
function getContainerHeight() {
    return Number($("#store-locations").css("height").replace("px", ""));
}

/*
    Returns the max up scroll offset.
*/
function getNavScrollUpHeightOffset() {
    // the height of the arrow and the add button
    return  -1*(getNavTotalHeight() - getContainerHeight() + NAV_SCROLL_BOTTOM_STATIC_HEIGHT);
}


function animateStop() {
    $("#store-locations > div.nav > a").stop();
}

function animateStart(direction) {
    $("#store-locations > div.nav > a").each(function() {
        var self = $(this);
        var top = Number(self.css("top").replace("px", ""));
        if (direction == "up") {
            top += 100;
            // prevent overscroll
            if (top > SCROLL_ARROW_HEIGHT) { 
                top = SCROLL_ARROW_HEIGHT;
            }
            
        } else {
            top -= 100;
            // prevent overscroll
            var maxOffset = getNavScrollUpHeightOffset();
            if (top < maxOffset) {
                top = maxOffset;
            } 
        
        }
            
        self.stop().animate({"top": String(top) + "px"}, ANIMATION_DURATION, function(){
            if (top != SCROLL_ARROW_HEIGHT && top != getNavScrollUpHeightOffset()) {
                animateStart(direction);
            }
            
        });
    });
}

function setActiveStoreLocation(storeLocationId) {
    $.ajax({
        url: $("#set_active_store_location_url").text()+"?store_location_id="+storeLocationId,
        type: "GET",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            // do nothing?
        },
    });
    
}

$(document).ready(function() {

    // clicks on nav items
    $("#store-locations > div.nav > a[class!=add]").click(function() {
        // activate this nav and deactive the rest
        var self = $(this);
        self.siblings().removeClass("active");
        self.addClass("active");
        
        // show the corresponding content and hide the rest
        var selfContent = $("#content-"+self.attr("id"));
        selfContent.siblings().removeClass("active");
        selfContent.addClass("active");
        
        // set active_store_location in server
        setActiveStoreLocation(self.attr("id"));
        
        return false;
    });
    
    
    // Hide the scroll arrows if scrolling is not yet enabled.
    if (getNavItemCount() < NAV_ITEM_SCROLL) {
        $("#store-locations > div.scroll").css("display", "none");
        // Show the add button in the nav item list and hide the one below the down arrow.
        $("#store-locations > div.nav > a.add").show();
        $("#store-locations > a.add").hide();
        return;
    } else {
        // Hide the add button in the nav item list and show the one below the down arrow.
        $("#store-locations > div.nav > a.add").hide();
        $("#store-locations > a.add").show();
    }
    
    // displace the nav item's initial position
    $("#store-locations > div.nav > a").css("top", SCROLL_ARROW_HEIGHT);
    
    // hover on up/down scroll
    $("#store-locations > div.scroll.up").hover(function() {
        animateStart("up");
        $(this).addClass("active");
        
    }, function() {
         animateStop();
        $(this).removeClass("active");
        
    });
    
     $("#store-locations > div.scroll.down").hover(function() {
        animateStart("down");
    }, function() {
         animateStop();
    });
    
    
});
