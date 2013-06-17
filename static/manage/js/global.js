$(document).ready(function(){
	$('div.th').click(function(){
		var el = $(this);
		var dir = 'asc';
		var matches = el.attr('id').match(/header-(.*)/);
		var col = matches[1];
		
		el.siblings().removeClass('sorted asc desc');
		el.addClass('sorted');
		
		if(el.hasClass('asc')){
			el.removeClass('asc');
			el.addClass('desc');
			dir = 'desc';
		} else {
			el.removeClass('desc');
			el.addClass('asc');
			dir = 'asc';
		}
		
		el.parent().siblings('.tr').tsort('.'+col,{order:dir});
		restripe(el.parent().siblings('.tr'));
	});
	
	$('div.tab').click(function(){
		var el = $(this);
		var matches = el.attr('id').match(/tab-(.*)/);
		var tab = matches[1];
		
		el.siblings().removeClass('active');
		el.addClass('active');
		
		$('.tab-body').removeClass('active');
		$('#tab-body-' + tab).addClass('active');
	});
	
	if($("div.notification.hide").length > 0)
	{
		setTimeout(function(){
		  $("div.notification.hide").animate({ height: 'toggle', opacity: 'toggle' }, 2500, function () {
		  $("div.notification.hide").remove();
		      });
		 
		}, 2500);
	}
});

function restripe(rows){
	rows.removeClass('odd');
	
	rows.each(function(index,el){
		if(++index % 2 == 1){
			$(el).addClass('odd');
		}
	});
}
