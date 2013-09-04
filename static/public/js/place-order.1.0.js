/*
    Script involving placing iPod Touch order form input.
    Tooltipster must be imported before this.
*/

$(document).ready(function(){

    $('.question_mark').tooltipster({
		    theme:'.re-punch'
	    });

    $("#place_order").click(function(){
        $("#place_order_span").toggle(this.checked);
        
        if (this.checked) {
            $("#cc_section").fadeIn("slow");
        } else {
            $("#cc_section").fadeOut("fast");
        }
        
    });
    
});
