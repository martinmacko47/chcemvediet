/* Enables elements to automatically show or hide other elements by bootstrap collapsing.
 * Works on all elements type, which must contain data-toggle="collapse" and
 * data-target="`css-selector`" attributes. Collapsable element must contain class="collapse".
 *
 * data-target-shown elements are shown, when collapsable elements are hidden. data-target-hidden
 * elements are shown, when collapsable elements are shown and vice versa.
 *
 * By entering url with a hash into browser, content and elements will be automatically collapsed.
 *
 * Requires:
 *  -- JQuery
 *
 * Examples:
 *  <div class="parent">
 *    <div data-toggle="collapse" data-target="#content">
 *      <p class="collapse-shown">Collapse</p>
 *      <p class="is-hidden collapse-hidden">Collapsed</p>
 *    </div>
 *    <p id="content" class="collapse" data-target-shown=".collapse-shown"
 *       data-target-hidden=".collapse-hidden" data-container=".question">
 *      Content
 *    </p>
 *  </div>
 */
$(function(){
	function collapse_show(){
		var container = $(this).data('container') || 'html';
		var target_shown = $.map(this.attributes, function(attr){
			if (attr.name.match("^data-target-shown")) return attr.value;
		}).join(', ');
		var target_hidden = $.map(this.attributes, function(attr){
			if (attr.name.match("^data-target-hidden")) return attr.value;
		}).join(', ');
		$(this).closest(container).find(target_shown).hide();
		$(this).closest(container).find(target_hidden).show();
	}
	function collapse_hide(){
		var container = $(this).data('container') || 'html';
		var target_shown = $.map(this.attributes, function(attr){
			if (attr.name.match("^data-target-shown")) return attr.value;
		}).join(', ');
		var target_hidden = $.map(this.attributes, function(attr){
			if (attr.name.match("^data-target-hidden")) return attr.value;
		}).join(', ');
		$(this).closest(container).find(target_shown).show();
		$(this).closest(container).find(target_hidden).hide();
	}
	$('.collapse').on('show.bs.collapse', collapse_show);
	$('.collapse').on('hide.bs.collapse', collapse_hide);
	$('[data-toggle="collapse"]').on('click', function(){
		if (this.id) {
			history.replaceState({}, '', '#' + this.id);
		}
	});
	$(window).on('ready hashchange', function(){
		var e = $(location.hash);
		if (e.data('toggle') === 'collapse') {
			$(e.attr('data-target')).collapse('show');
		}
	});
});
