$(function(){
	// Fix dropdown menu panel not to close when clicked.
	$('body').on('click', '.chv-dropdown-panel', function(event){
		event.stopPropagation();
	});

	// Alternative to ``data-dismiss`` to only hide target
	$('body').on('click', '[data-hide]', function(event){
		$(this).closest('.' + $(this).attr('data-hide')).hide();
	});
});
