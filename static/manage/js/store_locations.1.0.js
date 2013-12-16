/*
    Backend for the store locations list in store details.
*/


// the lower this number is, the faster the scroll will be
var ANIMATION_DURATION = 1000;

// The values below ust be synced with the values in store_locations.css
// need to know the height of a nav item (height + padding)
var NAV_ITEM_HEIGHT = 40 + 20;
// the amount of items before the scroll arrows are shown
var NAV_ITEM_SCROLL = 8;
// height of the scroll arrows (height + padding)
var SCROLL_ARROW_HEIGHT = 20 + 20;

function getNavItemCount() {
    return $("#store-locations > div.nav > a").length;
}

/*
    Returns the max up scroll offset.
*/
function getNavScrollUpHeightOffset() {
    // the height of the arrow and the add button
    var navBottomStaticHeight = SCROLL_ARROW_HEIGHT; // TODO add the button height
    return  -1*(getNavTotalHeight() - (NAV_ITEM_HEIGHT * NAV_ITEM_SCROLL) +
        navBottomStaticHeight);
}

function getNavTotalHeight() {
    return NAV_ITEM_HEIGHT * getNavItemCount();
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
                alert("animating");
            }
            
        });
    });
}


// TODO prevent overscroll
$(document).ready(function() {

    // clicks on nav items
    $("#store-locations > div.nav > a").click(function() {
        var self = $(this);
        self.siblings().removeClass("active");
        self.addClass("active");
    });
    
    
    // Hide the scroll arrows if passed NAV_ITEM_SCROLL
    if (getNavItemCount() < NAV_ITEM_SCROLL) {
        $("#store-locations > div.scroll").css("display", "none");
        return;
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
        $(this).addClass("active");
        
    }, function() {
         animateStop();
        $(this).removeClass("active");
        
    });
    
    
});
