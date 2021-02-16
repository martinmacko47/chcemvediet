/* Enables elements to automatically show or hide other elements by bootstrap collapsing.
 * Works on all elements type, which must contain ``data-toggle="collapse"`` and
 * ``data-target="css-selector"`` attributes. Collapsable element must contain ``collapse`` class.
 * Add ``hidden`` class to hide elements when loading the page.
 *
 * If element is collapsed, ``data-target-shown`` elements are displayed, ``data-target-hidden``
 * elements are hidden. Vice versa if element is expanded.
 *
 * When expanding element, location hash is updated to the value of ``data-hash``. Content and
 * elements are displayed automatically when opened using direct link.
 *
 * Requires:
 *  -- JQuery
 *
 * Examples:
 *  <div class="parent">
 *    <div data-toggle="collapse" data-target="#content">
 *      <p class="visible-if-collapsed">Collapsed</p>
 *      <p class="hidden visible-if-expanded">Expanded</p>
 *    </div>
 *    <p id="content" class="collapse" data-target-shown=".visible-if-collapsed"
 *       data-target-hidden=".visible-if-expanded" data-container=".parent" data-hash="content">
 *      Content
 *    </p>
 *  </div>
 */
$(function(){
	function collapse_show(){
		var container = $(this).data('container') || 'html';
		var target_shown = $(this).data('target-shown');
		var target_hidden = $(this).data('target-hidden');
		var hash = $(this).data('hash');
		$(this).closest(container).find(target_shown).addClass('hidden');
		$(this).closest(container).find(target_hidden).removeClass('hidden');
		if (hash) {
			history.replaceState({}, '', '#' + hash);
		}
	}
	function collapse_hide(){
		var container = $(this).data('container') || 'html';
		var target_shown = $(this).data('target-shown');
		var target_hidden = $(this).data('target-hidden');
		$(this).closest(container).find(target_shown).removeClass('hidden');
		$(this).closest(container).find(target_hidden).addClass('hidden');
	}
	$('.collapse').on('show.bs.collapse', collapse_show);
	$('.collapse').on('hide.bs.collapse', collapse_hide);
	$(window).on('ready hashchange', function(){
		var e = $(location.hash);
		if (e.data('toggle') === 'collapse') {
			$(e.data('target')).collapse('show');
		}
	});
});
