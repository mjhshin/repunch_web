$(document).ready(function(){

	$('#save-button').click(function(){
        if ($("#employee-saving").css("display") != "none") {
            return false;
        }
        $("#employee-saving").show();

        $('#employee-form').submit(); 
        return false;
    }); 

	// move to onclick to stopPropagation works?
	$('a#delete-button').click(function(event){
		
		return confirm("Are you sure you want to delete this employee?");
	});
	
	$('#load-more').click();
	
	$('.th').unbind('click').not('.not-sortable').click(function(){
		
		$this = $(this);
		if($this.hasClass('sorted')) //same column new direction
		{
			if($this.hasClass('desc'))
			{
				$this.removeClass('desc').addClass('asc');
				_order_dir = 'asc';
			}
			else
			{
				$this.removeClass('asc').addClass('desc');
				_order_dir = 'desc';
			}
		}
		else
		{
			$('.th.sorted').removeClass('sorted').removeClass('asc').removeClass('desc');
			$this.addClass('sorted desc');
			var id = $this.attr('id');
			
			var lastIndex = id.lastIndexOf('-');
			if(lastIndex != -1)
			{
				_order_by = id.substring(lastIndex+1); 
			}
			_order_dir = 'desc';
		}

		//remove all but the last row because it has the replacement
		$('.tr:not(:last-child)').remove();
		$('#table-body').html('<div class="tr" id="load-row"></div>');
		loadRow(1);
		return false;
	});
});

$.fn.loadWith = function(url, data){
    var c=$(this);
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        cache: false, // required to kill internet explorer 304 bug
        success: function(response){
            c.replaceWith(response);
        }
    });
        
};

function loadRow(page)
{
	var data = {order_by: _order_by, order_dir: _order_dir}
	$('#load-row').loadWith(_page_url+'?page='+page, data);
	return false;
}
