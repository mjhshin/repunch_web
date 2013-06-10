$(document).ready(function(){
	$('#link_refresh_retailer_pin').click(function(){
		
		try
		{
			$.post($(this).attr('href'), function(data) {
				if(data.success)
				{
					$('#retailer_pin').addClass('refreshed').html(data.retailer_pin);
				}
				else
				{
					alert("Error refreshing Retailer ID. Please contact your administrator.");
				}
			}, 'json');
		}
		catch(e)
		{
			alert("Error refreshing Retailer ID. Please contact your administrator.");
		}
		return false;
	});
});
