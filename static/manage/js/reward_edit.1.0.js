$(document).ready(function(){
	var loader = $("#reward-saving");
	$('#submit-reward-form').click(function(){
        if (!loader.is(":visible")){
            loader.show();
            $('#reward-form').submit(); 
        }
        return false;
    }); 
    
    
    // prevent cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
    });
    $('#delete-link').click(function(){
	    if (!loader.is(":visible")) {
		    return confirm("Are you sure you want to delete this Reward?");
		}
	});
	
});
