$(document).ready(function(){

    var loader = $("#settings-saving");
    $("#settings-form-submit").click(function(){
        if (!loader.is(":visible")){
	        loader.show();
            $('#settings-form').submit();
	    }
	    
        return false;
    });
    
    // prevent cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
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
