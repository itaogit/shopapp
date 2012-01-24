$(document).ready(function() {
	$('.custombox').click(function() {
		var thumb = $(this).parent('li').parent('span');
        var old_id = thumb.attr('id');
		if (old_id != 'featured') {
			var sthumb = '=s100';
			var slarge = '=s480';
			var copy_to = $('#featured').clone(true);
	        var img = $(this).find('img');
	        var newsrc = img.attr('src').replace(sthumb,slarge);
	        
	        img.attr('src',newsrc);
	        thumb.attr('id','featured');
	        img.width('480px');
	        img.height('360px');
	        $('#featured').replaceWith(thumb);
	        
	        copy_to.attr('id',old_id);
	        img = copy_to.find('img');
	        newsrc = img.attr('src').replace(slarge,sthumb);
	        img.attr('src',newsrc);
	        img.width('100px');
	        img.height('100px');
	        $('.media-grid').append(copy_to);
		}
		return false;
		});
});