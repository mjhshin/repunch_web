$(document).ready(function() {
	$('a#upload-avatar').click(function(e) {
		e.preventDefault();
		var $this = $(this);
		var href = $this.attr('href');
		
		var horizontalPadding = 0;
		var verticalPadding = 0;
		
		$('<iframe id="avatar-dialog" class="externalSite" src="' + href + '" frameborder="0" >').dialog({
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
			width: '350px'
		}).width('325px');

		return false;
	});
});

function cancelAvatarUpload() {
	$('#avatar-dialog').dialog('close');
	$('#avatar-dialog').remove();
}

function avatarUploadComplete() {
	$('#avatar-dialog').dialog('close');
	$('#avatar-dialog').remove();
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
