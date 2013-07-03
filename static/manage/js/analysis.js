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
	
	var jsonData = $.ajax({
          url: url,
          dataType:"json",
          async: false
          }).responseText;
          
  
  jsonData = $.parseJSON(jsonData);
	var options = {
        	legend: {position: 'bottom', alignment: 'start'},
        	//chartArea: { left: 0, top: 0},
        	width: 640,
        	height: 250,
        	pointSize: 4
        };
        

		//jsonData = [
        //  ['R', 'Male', 'Female', 'Unknown'],
        //  ['1/1/13 - 1/7/13',  1000, 1170, 660]
       // ]
        
      // Instantiate and draw our chart, passing in some options.
      breakdownGraph = new google.visualization.ColumnChart(document.getElementById('breakdown-graph'));
      breakdownGraph.draw(new google.visualization.arrayToDataTable(jsonData), options);

    $("#breakdown-loading").hide();

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
		
	var jsonData = $.ajax({
          url: url,
          dataType:"json",
          async: false
          }).responseText;
          
  

	var options = {
        	legend: {position: 'bottom', alignment: 'start'},
        	//chartArea: { left: 0, top: 0},
        	width: 640,
        	height: 250,
        	pointSize: 4
        };
      // Instantiate and draw our chart, passing in some options.
      trendsGraph = new google.visualization.LineChart(document.getElementById('trends-graph'));
      trendsGraph.draw(new google.visualization.DataTable(jsonData), options);
      
    $("#trends-loading").hide();

}
