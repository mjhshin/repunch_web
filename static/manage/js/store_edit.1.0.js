$(document).ready(function(){
	var loader = $(".form-options img");
	
	$('.form-options a.button.blue').click(function(){
        if (!loader.is(":visible")){
            loader.show();
            $('#store-edit-form').submit(); 
        }
        return false;
    }); 
    
    // prevent cancel
    $(".form-options a.red").click(function() {
        return !loader.is(":visible");
    });
    
});
