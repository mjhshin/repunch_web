$(document).ready(function() {
	$('a#crop-avatar').click(function(e) {
		e.preventDefault();
		var $this = $(this);
		var href = $this.attr('href');
		
		var horizontalPadding = 0;
		var verticalPadding = 0;
		
		$('<iframe id="avatar-crop-dialog" class="externalSite" src="' + href + '" frameborder="0" >').dialog({
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
			height: 390,
			width: 330,
		});

		return false;
	});
});

function cancelAvatarCrop() {
	$('#avatar-crop-dialog').dialog('close');
	$('#avatar-crop-dialog').remove();
}

function avatarCropComplete() {
	$('#avatar-crop-dialog').dialog('close');
	$('#avatar-crop-dialog').remove();
	// make an ajax call to retrieve the new store_avatar_url
	$.ajax({
        url: $("#get_store_avatar_url").val(),
        type: "GET",
        cache:false, // required to kill internet explorer 304 bug
        success: function(result) {
	        $("#store_avatar").attr("src", result);
        },
    });
}
