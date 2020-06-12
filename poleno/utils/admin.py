# vim: expandtab
# -*- coding: utf-8 -*-
from django.core.urlresolvers import NoReverseMatch
from django.utils.html import format_html, format_html_join
from django.contrib import admin

from poleno.utils.urls import reverse


def simple_list_filter_factory(filter_title, filter_parameter_name, filters):
    class SimpleListFilter(admin.SimpleListFilter):
        title = filter_title
        parameter_name = filter_parameter_name

        def lookups(self, request, model_admin):
            for value, label, func in filters:
                yield (value, label)

        def queryset(self, request, queryset):
            for value, label, func in filters:
                if self.value() == value:
                    return func(queryset)

    return SimpleListFilter

def admin_obj_format(obj, format=u'{tag}', *args, **kwargs):
    link = kwargs.pop(u'link', u'change')
    if obj is None:
        return u'--'
    tag = u'<{}: {}>'.format(obj.__class__.__name__, obj.pk)
    res = format.format(obj=obj, tag=tag, *args, **kwargs)
    if link:
        try:
            info = obj._meta.app_label, obj._meta.model_name, link
            url = reverse(u'admin:{}_{}_{}'.format(*info), args=[obj.pk])
            res = format_html(u'<a href="{0}">{1}</a>', url, res)
        except NoReverseMatch:
            pass
    return res

class ReadOnlyAdminInlineMixin(admin.options.InlineModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        return self.fields

    def has_change_permission(self, request, obj=None):
        u"""
        Returns True, only to display model on change view. The model can not be changed.
        """
        info = self.parent_model._meta.app_label, self.parent_model._meta.model_name
        url_name = u'{}_{}_change'.format(*info)
        return url_name == request.resolver_match.url_name

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
