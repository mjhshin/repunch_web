$(document).ready(function(){
	$('#send-now').click(function(){
		$('#action').val('send');
		$('#message-form').submit();
		return false;
	});
	
	$('#save-draft').click(function(){
		$('#action').val('draft');
		$('#message-form').submit();
		return false;
	});
	
	$('#upgrade').click(function(){
		$('#action').val('upgrade');
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
	
	$( "#id_date_offer_expiration" ).datetimepicker({
		timeFormat: "hh:mm tt"
	});
});
