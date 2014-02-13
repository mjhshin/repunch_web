
$(document).ready(function() {
	$('a.upload-image').click(function(e) {
		e.preventDefault();
		var $this = $(this);
		var href = $this.attr('href');
		
		$('<iframe name="image-upload-dialog" id="image-upload-dialog" class="externalSite" src="' + href + '" frameborder="0" style="padding:0px;padding:0px;">').dialog({
			autoOpen : true,
			modal : true,
			resizable : true,
			bgiframe : true,
			cache : false,
			position : ["center", "center"],
			overlay : {
				opacity : 1,
				background : "#000"
			}, 
		});

		return false;
	});
});

function resizeFrame(settings) {
    $('#image-upload-dialog').dialog(settings);
    $('#image-upload-dialog').css(settings);
    
    $('#image-upload-dialog').dialog({position : ["center", "center"]});
}

function imageCropComplete() {
	$('#image-upload-dialog').dialog('close');
	$('#image-upload-dialog').remove();
	// make an ajax call to retrieve the new image url
	$.ajax({
        url: $("#get_image_url").val(),
        type: "GET",
        cache:false, // required to kill internet explorer 304 bug
        success: function(result) {
	        $("#"+$("#get_image_id").val()).attr("src", result.src);
	        if (result.thumbnail) {
                $("#account-thumbnail").attr("src", result.src);
                $("#account-thumbnail").css("visibility", "visible");
            }
        },
    });
    
}

function cancelImageUpload() {
	$('#image-upload-dialog').dialog('close');
	$('#image-upload-dialog').remove();
}

