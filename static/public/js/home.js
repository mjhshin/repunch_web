/**
 *
 * Armando Borge
 * armando@cambiolabs.com
 * Re-Punch
 * March 2013
 *
 **/
$(document).ready(function()
{
	// Home slideshow
	$('#home-slideshow').slidesjs({
		width:960,
		height:540,
		navigation:{effect:'fade'},
		pagination:{effect:'fade'},
		effect:{
			fade:{speed: 400}
		}
	});		
});