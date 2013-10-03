/*
    Note that avatar_crop should b
*/

$(document).ready(function() {
	$('a#upload-avatar').click(function(e) {
		e.preventDefault();
		var $this = $(this);
		var href = $this.attr('href');
		
		$('<iframe name="avatar-dialog" id="avatar-dialog" class="externalSite" src="' + href + '" frameborder="0" style="padding:0px;padding:0px;">').dialog({
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
    $('#avatar-dialog').dialog(settings);
    $('#avatar-dialog').css(settings);
}

function avatarCropComplete() {
	$('#avatar-dialog').dialog('close');
	$('#avatar-dialog').remove();
	// make an ajax call to retrieve the new store_avatar_url
	$.ajax({
        url: $("#get_store_avatar_url").val(),
        type: "GET",
        cache:false, // required to kill internet explorer 304 bug
        success: function(result) {
	        $("#store_avatar").attr("src", result);
            $("#avatar-thumbnail").attr("src", result);
            $("#avatar-thumbnail").css("visibility", "visible");
        },
    });
    
}

function cancelAvatarUpload() {
	$('#avatar-dialog').dialog('close');
	$('#avatar-dialog').remove();
}

