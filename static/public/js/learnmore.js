/**
 *
 * Armando Borge
 * armando@cambiolabs.com
 * Re-Punch
 * March 2013
 *
 **/
$(document).ready(function()
{
	// Learn More tabs
	$('#learn-bottom-menu a').click(function()
	{
		var src = $('#learn-bottom-menu a.active img').attr('src');
			src = src.replace('orange','gray');
			
		$('#learn-bottom-menu a.active img').attr('src', src);
		$('#learn-bottom-menu a').removeClass('active');
		
		var id = $(this).attr('id');
		var src = $(this).find('img').attr('src');
			src = src.replace('gray','orange');
			
		$(this).find('img').attr('src', src);
		$(this).addClass('active');
				
		$('#learn-bottom-tabs-contents .tab').removeClass('active');
		$('#'+id+'Body').addClass('active');
		
		return false;
	});
});