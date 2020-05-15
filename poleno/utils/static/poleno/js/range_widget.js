/* Required for ``poleno.utils.forms.RangeWidget`` form widget.
 */

$(function(){
	function update(element){
		var slider = element.children('input').eq(0);
		var output = element.children('span').eq(0);
		output.html($(slider).val());
		slider.attr('value', $(slider).val());
	}
	function updateAll(){
		$('.pln-range-widget').each(function(){
			update($(this));
		});
	}

	$(document).on('input', '.pln-range-widget', function(event){
		update($(this));
	});
	$(document).on('pln-dom-changed', function(){ // Triggered by: poleno/js/ajax.js
		updateAll();
	});
	updateAll();
});
