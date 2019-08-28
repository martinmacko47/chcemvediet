# vim: expandtab
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

from poleno.utils.misc import decorate, filesize
from poleno.utils.admin import admin_obj_format
from poleno.attachments.views import download

from .models import (AttachmentNormalization, AttachmentRecognition, AttachmentAnonymization,
                     AttachmentFinalization)


@admin.register(AttachmentNormalization, site=admin.site)
class AttachmentNormalizationAdmin(admin.ModelAdmin):
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

    def download_view(self, request, attachment_normalization_pk):
        attachment_normalization = AttachmentNormalization.objects.get_or_404(
                pk=attachment_normalization_pk
        )
        return download(request, attachment_normalization)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        download_view = self.admin_site.admin_view(self.download_view)
        urls = patterns('',
                url(r'^(.+)/download/$', download_view, name=u'{}_{}_download'.format(*info)),
                )
        return urls + super(AttachmentNormalizationAdmin, self).get_urls()

@admin.register(AttachmentRecognition, site=admin.site)
class AttachmentRecognitionAdmin(admin.ModelAdmin):
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

    def download_view(self, request, attachment_recognition_pk):
        attachment_recognition = AttachmentRecognition.objects.get_or_404(
            pk=attachment_recognition_pk
        )
        return download(request, attachment_recognition)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        download_view = self.admin_site.admin_view(self.download_view)
        urls = patterns('',
                url(r'^(.+)/download/$', download_view, name=u'{}_{}_download'.format(*info)),
                )
        return urls + super(AttachmentRecognitionAdmin, self).get_urls()

@admin.register(AttachmentAnonymization, site=admin.site)
class AttachmentAnonymizationAdmin(admin.ModelAdmin):
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

    def download_view(self, request, attachment_anonymization_pk):
        attachment_anonymization = AttachmentAnonymization.objects.get_or_404(
            pk=attachment_anonymization_pk
        )
        return download(request, attachment_anonymization)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        download_view = self.admin_site.admin_view(self.download_view)
        urls = patterns('',
                url(r'^(.+)/download/$', download_view, name=u'{}_{}_download'.format(*info)),
                )
        return urls + super(AttachmentAnonymizationAdmin, self).get_urls()

@admin.register(AttachmentFinalization, site=admin.site)
class AttachmentFinalizationAdmin(admin.ModelAdmin):
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

    def download_view(self, request, attachment_finalization_pk):
        attachment_finalization = AttachmentFinalization.objects.get_or_404(
            pk=attachment_finalization_pk
        )
        return download(request, attachment_finalization)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        download_view = self.admin_site.admin_view(self.download_view)
        urls = patterns('',
                url(r'^(.+)/download/$', download_view, name=u'{}_{}_download'.format(*info)),
                )
        return urls + super(AttachmentFinalizationAdmin, self).get_urls()
