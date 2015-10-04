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
    tag = u'<%s: %s>' % (obj.__class__.__name__, obj.pk)
    res = format.format(obj=obj, tag=tag, *args, **kwargs)
    if link:
        try:
            info = obj._meta.app_label, obj._meta.model_name, link
            url = reverse(u'admin:%s_%s_%s' % info, args=[obj.pk])
            res = format_html(u'<a href="{0}">{1}</a>', url, res)
        except NoReverseMatch:
            pass
    return res
