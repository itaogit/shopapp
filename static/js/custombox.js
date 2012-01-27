$(document).ready(function() {
	$('.custombox').click(function() {
		var thumb = $(this).parent('li').parent('span').clone(true);
		thumb.find('img').css({"opacity": "1"});
		if (thumb.attr('id') != 'featured') {
	        var img = thumb.find('img');
	        var newsrc = img.attr('src').replace('=s100','=s480');
	        img.attr('src',newsrc);
	        thumb.attr('id','featured');
	        img.width('480px');
	        img.height('360px');
	        $('#featured').replaceWith(thumb);
	        $('span#thumb img').css({"opacity": "0.5"});
	        $(this).find('img').css({"opacity": "1"});
		}
		return false;
		});
});