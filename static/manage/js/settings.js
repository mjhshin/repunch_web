$(document).ready(function(){

    $("#settings-form-submit").click(function(){
        if ($("#settings-saving").css("display") != "none"){
	        return false;
	    }
	    $("#settings-saving").show();
    
        $('#settings-form').submit();
        return false;
    });

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
