$(document).ready(function(){
	$('#send-now').click(function(){
	    if ($("#message-sending").css("display") != "none"){
	        return false;
	    }
	    $("#message-sending").show();
	    
		$('#message-form').submit();
		return false;
	});
	
	$('#delete-button').click(function(){
		return confirm("Are you sure you want to delete this message?");
	});
	
	$('#id_attach_offer').change(function(){
		if(this.checked)
		{
			$('#offer-details').slideDown('slow');
		}
		else
		{
			$('#offer-details').slideUp('slow');
		}
	})
	
	if($( "#id_date_offer_expiration" ).length >0){
	    $( "#id_date_offer_expiration" ).datetimepicker({
	        timeFormat: "hh:mm tt"
	    });
    }
	
	/* This is in the html so that instead of ajaxing the min and max
	*  after page loads, the min and max are already provided at
	*  the time the server renders the page.
	// init the slider
	$( "#num_patrons_slider" ).slider({
        range: "min",
        value: 37,
        min: 1,
        max: 700,
        slide: function( event, ui ) {
        $( "#num_patrons" ).val( ui.value );
      }
    });
    */
    
    // span is hidden in the beginning
    $( "#num_patrons_span" ).find("*").hide();
	
	$( "#filter" ).mouseup(function(){
	    if ($(this).val() == "most_loyal"){
            $( "#num_patrons_span" ).find("*").fadeIn();
	    } else {
            $( "#num_patrons_span" ).find("*").fadeOut();
	    }
	});
	
});
