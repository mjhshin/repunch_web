$(document).ready(function(){
	$('#link_refresh_retailer_pin').click(function(){
	
	    var loading = $("#retailer-pin-loading");
		
		if(loading.css("display") != "none"){
		    return false;
		}
		
		loading.show();
		
		try
		{
			$.get($(this).attr('href'), function(data) {
				if(data.success)
				{
					$('#retailer_pin').addClass('refreshed').html(data.retailer_pin);
				}
				else
				{
					alert("Error refreshing Retailer ID. Please contact your administrator.");
				}
		        loading.hide();
			}, 'json');
		}
		catch(e)
		{
			alert("Error refreshing Retailer ID. Please contact your administrator.");
			loading.hide();
		}
		return false;
	});
});
