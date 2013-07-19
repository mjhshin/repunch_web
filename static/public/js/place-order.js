/*
    Script involving placing smartphone order form input.
*/

$(document).ready(function(){

    $("#place_order").click(function(){
        $("#place_order_span").toggle(this.checked);
        
        if (this.checked) {
            $("#cc_section").fadeIn("slow");
        } else {
            $("#cc_section").fadeOut("fast");
        }
        
    });
    
});
