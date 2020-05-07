/* Required for ``poleno.utils.forms.RangeWidget`` form widget.
 */

$(function(){
	$('.pln-range-widget').each(function(){
		var slider = $(this).children('input').eq(0);
		var output = $(this).children('span').eq(0);
		output.html($(slider).val());
		$(document).on('input', '.pln-range-widget input', function(event) {
			output.html($(slider).val());
		})
	});
});
