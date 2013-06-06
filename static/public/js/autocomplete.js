$(document).ready(function() {

    $( "#categories" ).autocomplete({
      source: function( request, response ) {
        $.ajax({
          url: "/categories",
          dataType: "jsonp",
          data: {
            featureClass: request.term,
          },
          success: function( data ) {
            response( $.map( data.geonames, function( item ) {
              return {
                label: item.name + (item.adminName1 ? ", " + item.adminName1 : "") + ", " + item.countryName,
                value: item.name
              }})); // end function
          }// end success
            
        }); // end ajax
      },// end source

      select: function( event, ui ) {
        log( ui.item ?
          "Selected: " + ui.item.label :
          "Nothing selected, input was " + this.value);
      },
      open: function() {
        $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
      },
      close: function() {
        $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
      }
    });

});
