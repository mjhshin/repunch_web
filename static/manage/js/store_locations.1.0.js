/*
    Backend for the store locations list in store details.
*/


// the lower this number is, the faster the scroll will be
var ANIMATION_DURATION = 1000;

$(document).ready(function() {
    // clicks on nav items
    $("#store-locations > div.nav > a").click(function() {
        var self = $(this);
        self.siblings().removeClass("active");
        self.addClass("active");
    });
    
    // hover on up/down scroll
    function animateStop() {
        $("#store-locations > div.nav > a").stop();
    }
    
    function animateStart(direction) {
        $("#store-locations > div.nav > a").each(function() {
            var self = $(this);
            var top = Number(self.css("top").replace("px", ""));
            if (direction == "up") {
                top = String(top+100) + "px";
            } else {
                top = String(top-100) + "px";
            }
                
            self.stop().animate({"top": top}, ANIMATION_DURATION, function(){
                animateStart(direction);
            });
        });
    }
    
    $("#store-locations > div.scroll.up").hover(function() {
        animateStart("up");
    }, function() {
         animateStop();
    });
    
     $("#store-locations > div.scroll.down").hover(function() {
        animateStart("down");
    }, function() {
         animateStop();
    });
    
});
