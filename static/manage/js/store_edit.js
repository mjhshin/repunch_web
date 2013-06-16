var start_count = 0;
var preview_start_count = 0;
$(document).ready(function(){
	
	// move to onclick to stopPropagation works?
	$('ul.hours-form li.days div').click(function(event){
		$this = $(this);
		
		if ($this.hasClass('active')){
		    $this.removeClass('active');
		} else {
		    // can only add active class if no other row of the same
		    // column is active. use the nth child selector!
		    var colNum = $this.attr('id');
		    colNum = colNum.charAt(colNum.length - 1);
		    colNum = new String(new Number(colNum) + 1);
		    // remove active from all the rows of the same column
		    $( "ul.hours-form li.days div:nth-child(" +
		        colNum + ").active" ).removeClass('active');
		    $this.addClass('active');
		}
		
		hoursPreview();
	});
	
	
	//attach preview to hours
	$("ul.hours-form select[name$='-open'], ul.hours-form select[name$='-close']").change(hoursPreview)
	
	
	var form_count = $('#id_hours-TOTAL_FORMS').val();
	start_count = form_count; //used for sending to server
	
	$('ul.hours-form li.buttons div.add').click(function(event){
		$this = $(this);
		
		// only add up to 7
		if ($('ul.hours-form').length > 7){
		    return;
		}
		
		var id = $this.attr('id');
		var prefix = id.substring(0, id.length-4);
		
		var clone = $('#clone-row').clone(true, true);
		$('[id^="clone"],[id^="id_clone"]', clone).each(function(){
			$this = $(this);
			var clone_id = $this.attr('id')
			var index = clone_id.indexOf('-')
			
			var newid = 'hours-' + form_count + clone_id.substring(index);
			$this.attr('id', newid).attr('name', newid);
		});
		$('#'+prefix+'-row').after(clone);
		clone.attr('id', 'hours-' + form_count + '-row').show();
		
		form_count++;
	});
	
	//remove the first remove button, need to  have at least one hours
	$('ul.django-form li.buttons div.remove').first().remove();	
	$('ul.hours-form li.buttons div.remove').click(function(event){
		$this = $(this);
		
		var id = $this.attr('id');
		var prefix = id.substring(0, id.length-7);
		
		if(confirm("Remove hours?"))
		{
			var row = $('#'+prefix+'-row');
			if(row.hasClass('django-form') == false)
			{
				row.remove();
			}
			else
			{
				$('#'+prefix+'-row').hide();				
				$('#id_'+prefix+'-DELETE').val('on');
			}
			
			hoursPreview();
		}
	});
	
	$('a#save-button').click(function(){
		var form = $('#account-edit-form');
		
		var count = 0;
		$('ul.hours-form').each(function(index){
			var row = $(this);
			var row_id = row.attr('id'); 
			if(row_id == 'clone-row')
			{
				return;
			}
			
			var prefix = '';
			//only update ids for cloned rows
			if(row.hasClass('django-form') == false)
			{
				//now we need to update the open and close
				$(":input", row).each(function(){
					var input = $(this);
					var id = input.attr('id');
					
					var last_index = id.lastIndexOf('-');
					if(last_index == -1)
					{
						return;
					}
					var postfix = id.substring(last_index);
					
					var newid = 'hours-' + start_count + postfix;
					input.attr('id', 'id_'+newid).attr('name', newid);
					
					if(postfix == '-list_order')
					{
						input.val(index+1);
					}
				});
				
				prefix = 'hours-'+start_count;
				start_count++;
			}
			else
			{
				var lastIndex = row_id.lastIndexOf('-');
				prefix = row_id.substring(0, lastIndex);
				
				$('#id_'+prefix+'-list_order').val(index+1);
			}
			
			//iterate through the days and create id
			$('li.days div.active', row).each(function(){
				
				var day = $(this);
				var id = day.attr('id');
				var dnum = parseInt(id.substring(id.length-1), 10);
				
				//form.append('<input type="hidden" name="id_hours-'+index+'-'+dnum+'" id="id_hours-'+index+'-'+dnum+'" value="'+(dnum+1)+'" />')
				form.append('<input type="hidden" name="'+prefix+'-days" id="id_'+prefix+'-days_'+dnum+'" value="'+(dnum+1)+'" />')
				
			});
			
			count = index;
		});
		
		//set form count
		$('#id_hours-TOTAL_FORMS').val(count+1);
		form.submit();
	});
	
	hoursPreview();
});


function hoursPreview()
{
	
	preview_start_count = start_count;
	var form = $('#account-edit-form');
	var data = {'hours-TOTAL_FORMS': $('#id_hours-TOTAL_FORMS').val(),
				'hours-INITIAL_FORMS': $('#id_hours-INITIAL_FORMS').val(),
				'hours-MAX_NUM_FORMS': $('#id_hours-MAX_NUM_FORMS').val()
				}
			
	var days_query = '';
	var count = 0;
	$('ul.hours-form').each(function(index){
		var row = $(this);
		var row_id = row.attr('id'); 
		if(row_id == 'clone-row')
		{
			return;
		}
		
		var prefix = '';
		//only update ids for cloned rows
		if(row.hasClass('django-form') == false)
		{
			//now we need to update the open and close
			$(":input", row).each(function(){
				var input = $(this);
				var id = input.attr('id');
				
				var last_index = id.lastIndexOf('-');
				if(last_index == -1)
				{
					return;
				}
				var postfix = id.substring(last_index);
				
				var newid = 'hours-' + preview_start_count + postfix;
				data[newid] = input.val()
				
				if(postfix == '-list_order')
				{
					data[newid] = index+1;
				}
			});
			
			prefix = 'hours-'+preview_start_count;
			preview_start_count++;
		}
		else
		{
			var lastIndex = row_id.lastIndexOf('-');
			prefix = row_id.substring(0, lastIndex);
			
			$(":input", row).each(function(){
				var input = $(this);
				var name = input.attr('name');				
				
				data[name] = input.val()
				if(name.indexOf('-list_order') != -1)
				{
					data[name] = index+1;
				}
			});
		}
		
		
		//iterate through the days and create id
		$('li.days div.active', row).each(function(){
			
			var day = $(this);
			var id = day.attr('id');
			var dnum = parseInt(id.substring(id.length-1), 10);
			
			days_query += prefix+'-days='+(dnum+1)+'&';			
		});
		
		count = index;
	});
	
	
	data['hours-TOTAL_FORMS'] = count+1;
	$('#store-hours-preview').load(_hours_preview_url, days_query+$.param(data))
}
