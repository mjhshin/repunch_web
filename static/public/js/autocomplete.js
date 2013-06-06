$(document).ready(function() {
    var box = $("#categories-box");

    $( "#categories" ).autocomplete({
      source: "/categories",
      messages: {
          noResults: '',
          results: function() {}
      },
      select: function( event, ui ) {
        if ($(".closable-box").length > 1){
            $(".closable-box").first().remove();
        }
        box.append("<span class='closable-box'>" +
                  ui.item.value  + "</span>");
        $(".closable-box").click(function(){
            $(this).remove()
        });
      }, 
    });

});
