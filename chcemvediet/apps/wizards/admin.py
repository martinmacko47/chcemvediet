# vim: expandtab
# -*- coding: utf-8 -*-
from django.contrib import admin

from poleno.utils.misc import decorate
from poleno.utils.admin import admin_obj_format

from .models import WizardDraft


@admin.register(WizardDraft, site=admin.site)
class WizardDraftAdmin(admin.ModelAdmin):
    date_hierarchy = u'modified'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.owner,
                    u'{obj.first_name} {obj.last_name} <{obj.email}>'),
                short_description=u'Owner',
                admin_order_field=u'owner__email',
                ),
            u'step',
            u'modified',
            ]
    list_filter = [
            u'modified',
            ]
    search_fields = [
            u'id', # ID contains wizard name
            u'owner__first_name',
            u'owner__last_name',
            u'owner__email',
            u'step',
            ]
    ordering = [
            u'id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'owner',
            ]
    inlines = [
            ]
    actions = [
            u'delete_selected',
    ]

    def get_queryset(self, request):
        queryset = super(WizardDraftAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'owner')
        return queryset
