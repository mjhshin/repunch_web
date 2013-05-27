$(document).ready(function(){
	$('#link_refresh_retailer_id').click(function(){
		
		try
		{
			$.post($(this).attr('href'), function(data) {
				if(data.success)
				{
					$('#retailer_id').addClass('refreshed').html(data.retailer_id);
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
