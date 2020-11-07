# vim: expandtab
# -*- coding: utf-8 -*-
from django.contrib import admin

from poleno.attachments.admin import DownloadAdminMixin
from poleno.utils.misc import decorate, filesize
from poleno.utils.admin import admin_obj_format

from .models import (AttachmentNormalization, AttachmentRecognition, AttachmentAnonymization,
                     AttachmentFinalization)


@admin.register(AttachmentNormalization, site=admin.site)
class AttachmentNormalizationAdmin(DownloadAdminMixin, admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.attachment, u'{obj}'),
                short_description=u'Attachment',
                admin_order_field=u'attachment',
            ),
            u'successful',
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
            u'successful',
            ]
    search_fields = [
            u'=id',
            u'file',
            u'name',
            u'content_type',
            u'debug',
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

@admin.register(AttachmentRecognition, site=admin.site)
class AttachmentRecognitionAdmin(DownloadAdminMixin, admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.attachment, u'{obj}'),
                short_description=u'Attachment',
                admin_order_field=u'attachment',
            ),
            u'successful',
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
            u'successful',
            ]
    search_fields = [
            u'=id',
            u'file',
            u'name',
            u'content_type',
            u'debug',
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

@admin.register(AttachmentAnonymization, site=admin.site)
class AttachmentAnonymizationAdmin(DownloadAdminMixin, admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.attachment, u'{obj}'),
                short_description=u'Attachment',
                admin_order_field=u'attachment',
            ),
            u'successful',
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
            u'successful',
            ]
    search_fields = [
            u'=id',
            u'file',
            u'name',
            u'content_type',
            u'debug',
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

@admin.register(AttachmentFinalization, site=admin.site)
class AttachmentFinalizationAdmin(DownloadAdminMixin, admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.attachment, u'{obj}'),
                short_description=u'Attachment',
                admin_order_field=u'attachment',
            ),
            u'successful',
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
            u'successful',
            ]
    search_fields = [
            u'=id',
            u'file',
            u'name',
            u'content_type',
            u'debug',
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
