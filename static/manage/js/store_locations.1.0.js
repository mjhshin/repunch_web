/*
    Backend for the store locations list in store details and global header.
*/

// ids
var HEADER_CONTAINER_ID = "store-locations-header"
var CONTAINER_ID = "store-locations"

// the lower this number is, the faster the scroll will be
var ANIMATION_DURATION = 1000;
var DIR_UP = 0, DIR_DOWN=1;

// The values below ust be synced with the values in store_locations.css
// need to know the height of a nav item (height + padding + border)
var NAV_ITEM_HEIGHT = 40 + 20 + 1;
// need to know the height of the active nav item (height + padding + border)
var NAV_ITEM_ACTIVE_HEIGHT = 70 + 20 + 1;
// the amount of items before the scroll arrows are shown
var NAV_ITEM_SCROLL = 8;
// height of the scroll arrows (height + padding)
var SCROLL_ARROW_HEIGHT = 10 + 10;
// height of the add button (height + padding)
var ADD_BUTTON_HEIGHT = 60 + 20;
// Total height of the add button and the arrow down when scrolling is enabled.
var NAV_SCROLL_BOTTOM_STATIC_HEIGHT = SCROLL_ARROW_HEIGHT + ADD_BUTTON_HEIGHT;

/* NAV HEADER SPECIFICS */
// the amount of items before the scroll arrows are shown
var HEADER_NAV_ITEM_SCROLL = 4;
// Static height at the bottom of the list when scrolling is enabled.
// added 70 to this because of the offset from the header
var HEADER_NAV_SCROLL_BOTTOM_STATIC_HEIGHT = SCROLL_ARROW_HEIGHT + 70;

function isInStoreDetails() {
    return $("#"+CONTAINER_ID).length > 0;
}


/*
    Does not include the add button.
*/
function getNavItemCount(containerId) {
    return $("#"+containerId+" > div.nav > a[class!=add]").length;
}

/*
    One of the item is active (different height in body but not in header).
*/
function getNavTotalHeight(containerId) {
    return (NAV_ITEM_HEIGHT * getNavItemCount(containerId)) -
        NAV_ITEM_HEIGHT + (containerId == CONTAINER_ID ? NAV_ITEM_ACTIVE_HEIGHT : NAV_ITEM_HEIGHT);
}

/*
    The Root container height.
*/
function getContainerHeight(containerId) {
    return Number($("#"+containerId).css("height").replace("px", ""));
}

function getScrollBottomStaticHeight(containerId){
    if (containerId == CONTAINER_ID) {
        return NAV_SCROLL_BOTTOM_STATIC_HEIGHT;
    } else {
        return HEADER_NAV_SCROLL_BOTTOM_STATIC_HEIGHT;
    }
}

function getScrollThreshold(containerId) {
    if (containerId == CONTAINER_ID) {
        return NAV_ITEM_SCROLL;
    } else {
        return HEADER_NAV_ITEM_SCROLL;
    }
}

/*
    Returns the max up scroll offset.
*/
function getScrollUpHeightOffset(containerId) {
    // the height of the arrow and the add button
    return  -1*(getNavTotalHeight(containerId) -
        getContainerHeight(containerId) + getScrollBottomStaticHeight(containerId));
}

function animateStop(containerId) {
    $("#"+containerId+" > div.nav > a").stop();
}

function animateStart(containerId, direction) {
    $("#"+containerId+" > div.nav > a").each(function() {
        var self = $(this);
        var top = Number(self.css("top").replace("px", ""));
        if (direction == DIR_UP) {
            top += 100;
            // prevent overscroll
            if (top > SCROLL_ARROW_HEIGHT) { 
                top = SCROLL_ARROW_HEIGHT;
            }
            
        } else {
            top -= 100;
            // prevent overscroll
            var maxOffset = getScrollUpHeightOffset(containerId);
            if (top < maxOffset) {
                top = maxOffset;
            } 
        
        }
            
        self.stop().animate({"top": String(top) + "px"}, ANIMATION_DURATION, function(){
            if (top != SCROLL_ARROW_HEIGHT && top != getScrollUpHeightOffset(containerId)) {
                animateStart(containerId, direction);
            }
            
        });
    });
}

function setActiveStoreLocation(containerId, storeLocationId) {

    $.ajax({
        url: $("#set_active_store_location_url").text()+"?store_location_id="+storeLocationId,
        type: "GET",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            // replace the header current div
            $("#"+HEADER_CONTAINER_ID+" > div.current").html("<span></span>" +
                $("#header-"+storeLocationId).html().replace("<span></span>", "")
                    .replace("<div>", "").replace("</div>", ""));
            
            // if the click was from the header, reload page content
            if (containerId == HEADER_CONTAINER_ID && !isInStoreDetails()) {
                location.reload(true);
            }
            
        },
    });
    
}

/*
    This is where the magic happens.
*/
function toStoreLocations(containerId) {
    // clicks on nav items
    $(".store-locations > div.nav > a[class!=add]").click(function() {
        var self = $(this);
        
        // do nothing if it's already active
        if (self.hasClass("active")){
            return false;
        }
        
        // show the corresponding content and hide the rest
        var storeLocationId = self.attr("id").replace( containerId == CONTAINER_ID ? "navcontent-" : "header-", "");
    
        // activate this row and deactive the rest
        $(".store-locations > div.nav > a[class!=add]").removeClass("active");
        $("#header-"+storeLocationId).addClass("active");
        
        if (isInStoreDetails()) {
            $("#navcontent-"+storeLocationId).addClass("active");
        
            var selfContent = $("#content-"+storeLocationId);
            selfContent.siblings().removeClass("active");
            selfContent.addClass("active");
        }
        
        // set active_store_location in server
        setActiveStoreLocation(containerId, storeLocationId);
        
        return false;
    });
    
    
    // Hide the scroll arrows if scrolling is not yet enabled.
    if (getNavItemCount(containerId) < getScrollThreshold(containerId)) {
        $("#"+containerId+" > div.scroll").css("display", "none");
        // Show the add button in the nav item list and hide the one below the down arrow.
        $("#"+containerId+" > div.nav > a.add").show();
        $("#"+containerId+" > a.add").hide();
        return;
    } else {
        // Hide the add button in the nav item list and show the one below the down arrow.
        $("#"+containerId+" > div.nav > a.add").hide();
        $("#"+containerId+" > a.add").show();
    }
    
    // displace the nav item's initial position
    $("#"+containerId+" > div.nav > a").css("top", SCROLL_ARROW_HEIGHT);
    
    // hover on up/down scroll
    $("#"+containerId+" > div.scroll.up").hover(function() {
        animateStart(containerId, DIR_UP);
        $(this).addClass("active");
        
    }, function() {
         animateStop(containerId);
        $(this).removeClass("active");
        
    });
    
     $("#"+containerId+" > div.scroll.down").hover(function() {
        animateStart(containerId, DIR_DOWN);
    }, function() {
         animateStop(containerId);
    });
    
}

$(document).ready(function() {

    // the header store locations
    toStoreLocations(HEADER_CONTAINER_ID);
    
    // the store_details store locations
    if (isInStoreDetails()) {
        toStoreLocations(CONTAINER_ID);
    }
    
});
