$(document).ready(function(){
    var loader = $("#message-sending");
	$('#send-now').click(function(){
	    if (!loader.is(":visible")){
	        $("#message-sending").show();
		    $('#message-form').submit();
	    }
	    
		return false;
	});
	
    // prevent cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
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
    
    // spans are hidden in the beginning
    $( "#num_patrons_span" ).find("*").hide();
    $( "#idle_latency_span" ).find("*").hide();
	
	$( "#filter" ).change(function(){
        var option = $("#filter option:selected").val();
	    if (option == "most_loyal"){
            $( "#num_patrons_span" ).find("*").fadeIn();
	    } else {
            $( "#num_patrons_span" ).find("*").fadeOut();
	    }
	    if (option == "idle") {
            $( "#idle_latency_span" ).find("*").fadeIn();
	    } else {
            $( "#idle_latency_span" ).find("*").fadeOut();
	    }
	    
	});
	
});
