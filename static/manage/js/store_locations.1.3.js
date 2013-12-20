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
// Total height of the add button when scrolling is enabled.
var NAV_SCROLL_BOTTOM_STATIC_HEIGHT = ADD_BUTTON_HEIGHT;

/* NAV HEADER SPECIFICS */
// the amount of items before the scroll arrows are shown
var HEADER_NAV_ITEM_SCROLL = 4;
// Static height at the bottom of the list when scrolling is enabled.
// this is 70 because of the offset from the header
var HEADER_NAV_SCROLL_BOTTOM_STATIC_HEIGHT = 70;

/*
    Also used by comet.js
*/
function isInStoreDetails() {
    return $("#"+CONTAINER_ID).length > 0;
}

function isInStoreLocationEdit() {
    return $("#in-storelocation-edit").length > 0;
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

/*
    Checks if the first row in the list has reached max up/down scroll.
    This will reanimate in the direction given if direction is provided and
    the list has not yet reached its max scroll in that direction.
*/
function animateComplete(containerId, top, direction) {
    // reached the top - hide the arrow up
    if (top == 0) {
        $("#"+containerId+" > div.scroll.up").fadeOut();
    } else {
        $("#"+containerId+" > div.scroll.up").fadeIn();
    }
    
    // reached the bottom - hide the arrow down
    if (top == getScrollUpHeightOffset(containerId)) {
        $("#"+containerId+" > div.scroll.down").fadeOut();
    } else {
        $("#"+containerId+" > div.scroll.down").fadeIn();
    }
    
    // animate and show both arrows
    if (direction != null && top != 0 && top != getScrollUpHeightOffset(containerId)){
        $("#"+containerId+" > div.scroll").fadeIn();
        animateStart(containerId, direction);
    }
}

/*
    Stops the animation of all items in the list and calls animateComplete without direction.
*/
function animateStop(containerId) {
    $("#"+containerId+" > div.nav > a").stop();
    animateComplete(containerId, Number($("#"+containerId+" > div.nav > a:first-child").css("top").replace("px", "")));
}

function animateStart(containerId, direction) {
    $("#"+containerId+" > div.nav > a").each(function() {
        var self = $(this);
        var top = Number(self.css("top").replace("px", ""));
        if (direction == DIR_UP) {
            top += 100;
            // prevent overscroll
            if (top > 0) { 
                top = 0;
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
            // check if we should animate again and the visibility of the scroll arrows
            if (!self.is(":first-child")) {
                animateComplete(containerId, top, direction);
            }     
           
        });
    });
}

function setActiveStoreLocationInHeader(storeLocationId) {
    // replace the header current div
    $("#"+HEADER_CONTAINER_ID+" > div.current").html("<span></span>" +
        $("#header-"+storeLocationId).html().replace("<span></span>", "")
            .replace("<div>", "").replace("</div>", ""));
}

function setActiveStoreLocation(containerId, storeLocationId) {
    var reloadPage = containerId == HEADER_CONTAINER_ID && !isInStoreDetails();
    
    if (reloadPage) {
        $(".store-locations.header").addClass("reloading");
    }
    
    setActiveStoreLocationInHeader(storeLocationId);

    $.ajax({
        url: $("#set_active_store_location_url").text()+"?store_location_id="+storeLocationId,
        type: "GET",
        cache: false, // required to kill internet explorer 304 bug
        success: function(res) {
            // if the click was from the header, reload page content
            if (reloadPage) {
                var url = document.URL;
                if (isInStoreLocationEdit()) {
                    url = url.replace(/edit-location\/.+/, "edit-location/"+storeLocationId);
                }
                
                // this does not create history
                window.location.replace(url);
            }
            
        },
    });
    
}

/*
    Used by comet.js if in store details page.
    Since a refresh does not occur in the store detaiils page
    when the store location id changes, we do it here.
    This does not make a set store location id request.
*/
function setActiveStoreLocationInStoreDetails(storeLocationId) {
    setActiveStoreLocationInHeader(storeLocationId);
    $(".store-locations > div.nav > a[class!=add]").removeClass("active");
    $("#header-"+storeLocationId+", #navcontent-"+storeLocationId).addClass("active");
    
    var selfContent = $("#content-"+storeLocationId);
    selfContent.siblings().removeClass("active");
    selfContent.addClass("active");
}

/*
    This is where the magic happens.
*/
function toStoreLocations(containerId) {
    // clicks on nav items
    $("#"+containerId+" > div.nav > a[class!=add]").click(function() {
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
        return;
    }
    
    // hide the scroll up arrow initially since the list top is 0
    $("#"+containerId+" > div.scroll.up").hide();
    
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
