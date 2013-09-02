$(document).ready(function(){
	$('#delete-link').click(function(){
		return confirm("Are you sure you want to delete this Reward?");
	});
	
	$('#submit-reward-form').click(function(){
        if ($("#reward-saving").css("display") != "none"){
            return false;
        }
        $("#reward-saving").show();

        $('#reward-form').submit(); 
        return false;
    }); 
});
