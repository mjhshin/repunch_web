$(document).ready(function(){
	// move to onclick to stopPropagation works?
	$('.graph input').click(function(event){
		// return false;
	});
	
	$('.remove img').click(function(event){
		
		return confirm("Are you sure you want to remove this employee?");
	});
	
	$('a.employee.approve').click(function(event){
		
		return confirm("Approve employee?");
	});
	
	$('a.employee.deny').click(function(event){
		
		return confirm("Deny employee?");
	});
	
	
	$("[name='employee-graph-cb']").click(function(){
		updateChart();
	})
	
	//tie date selectors to chart
	$( "#graph-dates > input" ).datepicker({ autoSize: true, onSelect: function(dateText, inst){
		updateChart();
	} });
});

var chart = null;
function updateChart()
{
	var start = $('#graph-start-date').val();
	var end = $('#graph-end-date').val();
	
	//validate that start and end dates are correct
	var start_date = $.datepicker.parseDate( "mm/dd/yy", start);
	var end_date = $.datepicker.parseDate( "mm/dd/yy", end);
	if(start_date > end_date)
	{
		alert("Error: Start date must come before your end date.");
		return;
	}
	
	var data = {'employee': []}
	$("input:checked").each(function() 
	{
	   data['employee'].push($(this).val());
	});
	
	if(data.employee.length == 0)
	{
		if(chart != null)
		{
			chart.clearChart();
			$('#employee-chart').html('<p>Please select an employee to start graphing...</p>');
		}
		return;// don't graph until we have emloyees
	}
	
	data.start= start;
	data.end = end;
	
	
	$.ajax({
        url: _graph_url,
        type: "GET",
        dataType:"json",
        data: data,
        cache: false, // required to kill internet explorer 304 bug
        success: function(jsonData){
            var options = {
                	legend: {position: 'bottom', alignment: 'start'},
                	//chartArea: { left: 0, top: 0},
                	width: 640,
                	height: 250,
                	pointSize: 4,
                	animation:{
                        duration: 1000,
                        easing: 'out'
                    },
                	tooltip: {
                	    showColorCode: true,
                	    isHtml: true,
                	},
                };
              // Instantiate and draw our chart, passing in some options.
              if (chart == null) {
                chart = new google.visualization.LineChart(document.getElementById('employee-chart'));
              }
              chart.draw(new google.visualization.DataTable(jsonData), options);
        }
    });

}
