$(document).ready(function(){
	$('#send-now').click(function(){
		$('#status').val('Sent');
		$('#message-form').submit();
		return false;
	});
	
	$('#save-draft').click(function(){
		$('#status').val('Draft');
		$('#message-form').submit();
		return false;
	});
	
	$('#delete-button').click(function(){
		return confirm("Are you sure you want to delete this feedback thread?")
	});
});
