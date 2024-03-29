$(document).ready(function(){
	//tie date selectors to chart
	$( "#trends-type" ).change(updateTrendsGraph);
	$( "#trends-dates > input" ).datepicker({ autoSize: true, onSelect: updateTrendsGraph});
	
	$( "#breakdown-container select" ).change(updateBreakdownGraph);
});


var breakdownGraph = null;
function updateBreakdownGraph()
{	
    $("#breakdown-loading").show();

	var url = _breakdown_graph_url + $('#breakdown-type').val() + '/' + 
	$('#breakdown-filter').val() + '/' + 
	$('#breakdown-range').val() + '/';
	
	$.ajax({
        url: url,
        type: "GET",
        cache:false, // required to kill internet explorer 304 bug
        success: function(jsonData){
            if (jsonData.hasOwnProperty("error")){
                alert(jsonData.error);
                $("#breakdown-loading").hide();
                return;
            }
        
            var options = {
                	legend: {position: 'bottom', alignment: 'start'},
                	//chartArea: { left: 0, top: 0},
                	width: 640,
                	height: 250,
                	animation:{
                        duration: 1000,
                        easing: 'out'
                    },
                	tooltip: {
                	    showColorCode: true,
                	    isHtml: true,
                	},
                };
                

            //jsonData = [
            //  ['R', 'Male', 'Female', 'Unknown'],
            //  ['1/1/13 - 1/7/13',  1000, 1170, 660]
            // ]
                
            // Instantiate and draw our chart, passing in some options.
            if (breakdownGraph == null) {
                breakdownGraph = new google.visualization.ColumnChart(document.getElementById('breakdown-graph'));
            }
            
            var dataTable = new google.visualization.arrayToDataTable(jsonData);
            breakdownGraph.draw(dataTable, options);

            $("#breakdown-loading").hide();
	    },
    });

}


var trendsGraph = null;
function updateTrendsGraph()
{
    $("#trends-loading").show();

	var start = $('#trends-start-date').val();
	var end = $('#trends-end-date').val();
	
	//validate that start and end dates are correct
	var start_date = $.datepicker.parseDate( "mm/dd/yy", start);
	var end_date = $.datepicker.parseDate( "mm/dd/yy", end);
	if(start_date > end_date)
	{
		alert("Error: Start date must come before your end date.");
		return;
	}
		
	var url = _trends_graph_url + $('#trends-type').val() + '/' + 
	$.datepicker.formatDate( "yy-mm-dd", start_date) + '/' + 
	$.datepicker.formatDate( "yy-mm-dd", end_date) + '/';
	
	$.ajax({
        url: url,
        type: "GET",
        cache: false, // required to kill internet explorer 304 bug
        success: function(jsonData){
            if (jsonData.hasOwnProperty("error")){
                alert(jsonData.error);
                $("#trends-loading").hide();
                return;
            }
            
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
            if (trendsGraph == null) {
                trendsGraph = new google.visualization.LineChart(document.getElementById('trends-graph'));
            }
            trendsGraph.draw(new google.visualization.DataTable(jsonData), options);

            $("#trends-loading").hide();
	    }
    });

}
