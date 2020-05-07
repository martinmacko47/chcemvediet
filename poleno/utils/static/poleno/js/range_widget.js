/* Required for ``poleno.utils.forms.RangeWidget`` form widget.
 */

$(function(){
	$('.pln-range-widget').each(function(){
		var slider = $(this).children('input').eq(0);
		var output = $(this).children('span').eq(0);
		output.html($(slider).val());
           $(slider).on('input', valueUpdated);
           function valueUpdated (e) {
               output.html($(slider).val());
           }
	});
});
