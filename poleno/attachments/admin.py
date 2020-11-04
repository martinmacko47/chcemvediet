# vim: expandtab
# -*- coding: utf-8 -*-
from django.contrib import admin

from poleno.utils.misc import decorate, filesize
from poleno.utils.admin import admin_obj_format, DownloadAdminMixin

from .models import Attachment


@admin.register(Attachment, site=admin.site)
class AttachmentAdmin(DownloadAdminMixin, admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.generic_object),
                short_description=u'Generic Object',
                admin_order_field=u'generic_type__name',
                ),
            decorate(
                lambda o: admin_obj_format(o, u'{obj.file.name}', link=u'download'),
                short_description=u'File',
                admin_order_field=u'file',
                ),
            u'name',
            u'content_type',
            u'created',
            decorate(
                lambda o: filesize(o.size),
                short_description=u'Size',
                admin_order_field=u'size',
                ),
            ]
    list_filter = [
            u'created',
            u'content_type',
            u'generic_type',
            ]
    search_fields = [
            u'=id',
            u'=generic_id',
            u'generic_type__name',
            u'file',
            u'name',
            u'content_type',
            ]
    ordering = [
            u'-id',
            ]
    exclude = [
            u'file',
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            ]
    inlines = [
            ]

    def get_queryset(self, request):
        queryset = super(AttachmentAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related(u'generic_object')
        return queryset
