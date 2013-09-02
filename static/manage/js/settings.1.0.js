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
		    $.ajax({
                url: $(this).attr('href'),
                type: "GET",
                cache:false, // required to kill internet explorer 304 bug
                success: function(data) {
                    if (data.hasOwnProperty("error")) {
                        alert(data.error);
                        loading.hide();
                        return;
                    }   
                                    
				    if(data.success) {
					    $('#retailer_pin').addClass('refreshed').html(data.retailer_pin);
				    } else {
					    alert("Error refreshing Retailer ID. Please contact your administrator.");
				    }
		            loading.hide();
			    }
		    });
		}
		catch(e)
		{
			alert("Error refreshing Retailer ID. Please contact your administrator.");
			loading.hide();
		}
		return false;
	});
	
});
