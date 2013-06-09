$(document).ready(function() {
    var box = $("#categories-box");

    function reset() {
        $(".closable-box").last().css('left', '-35px');
        $(".closable-box").first().css('left', '0px');
    }

    function resetX() {
        $(".close-xtag").last().css('left', '-65px');
        $(".close-xtag").first().css('left', '-35px');
    }

    $( "#categories" ).autocomplete({
      source: "/categories",
      messages: {
          noResults: '',
          results: function() {}
      },
      select: function( event, ui ) {
        if ($(".closable-box").length > 2){
            $(".closable-box").first().remove();
            $(".close-xtag").first().remove()
            reset(); resetX();
            $(".closable-box").first().fadeOut(1000, function(){
                $(this).remove();
                reset();
            });
            $(".close-xtag").first().fadeOut(1000, function(){
                $(this).remove();
                resetX();
            });
        } else if ($(".closable-box").length > 1){
            $(".closable-box").first().fadeOut(1000, function(){
                $(this).remove();
                reset();
            });
            $(".close-xtag").first().fadeOut(1000, function(){
                $(this).remove();
                resetX();
            });
        }
        // add the box
        box.append("<span class='closable-box'>" +
                  ui.item.value  + "</span>" +
                  "<span class='close-xtag'>X</span>");
        // add the event handlers
        $(".close-xtag").click(function(){
            $(this).fadeOut(1000, function(){
                $(this).remove();
            });
            $(this).prev().fadeOut(1000, function(){
                $(this).remove();
            });
        });
        // make sure that the appended has correct left value
        if ($(".closable-box").length > 2) {
            $(".closable-box").last().css('left', '-65px');
            $(".close-xtag").last().css('left', '-95px');
        } else if ($(".closable-box").length > 1) {
            $(".closable-box").last().css('left', '-35px');
            $(".close-xtag").last().css('left', '-65px');
        }

        // clear the input field
        $( "#categories" ).val(" ");

      }, 
    });

    // format value of categories before submition
    $("#signup-form").submit(function(){
        var cats = ''
        $(".closable-box").each(function(){
            cats = cats + $(this).text() + ',';
        });
        $( "#categories" ).val(cats);
        alert($( "#categories" ).val());
        return true;
    });

});
