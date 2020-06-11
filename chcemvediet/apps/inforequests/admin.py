# vim: expandtab
# -*- coding: utf-8 -*-
from django.contrib import admin

from poleno.utils.misc import decorate
from poleno.utils.admin import (simple_list_filter_factory, admin_obj_format,
                                ReadOnlyAdminInlineMixin)

from .models import Inforequest, InforequestDraft, InforequestEmail, Branch, Action


class BranchInline(ReadOnlyAdminInlineMixin, admin.TabularInline):
    model = Branch
    fields = [
            decorate(
                lambda o: admin_obj_format(o, u'{obj.pk}'),
                short_description=u'id',
                ),
            decorate(
                lambda o: admin_obj_format(o.obligee, u'{obj.name}'),
                short_description=u'obligee',
                ),
            ]

@admin.register(Inforequest, site=admin.site)
class InforequestAdmin(admin.ModelAdmin):
    date_hierarchy = u'submission_date'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.applicant,
                    u'{obj.first_name} {obj.last_name} <{obj.email}>'),
                short_description=u'Applicant',
                admin_order_field=u'applicant__email',
                ),
            decorate(
                lambda o: admin_obj_format(o.main_branch.obligee, u'{obj.name}'),
                short_description=u'Obligee',
                admin_order_field=u'branch__obligee__name',
                ),
            u'subject',
            u'submission_date',
            decorate(
                lambda o: o.undecided_emails_count,
                short_description=u'Undecided E-mails',
                admin_order_field=u'undecided_emails_count',
                ),
            u'closed',
            u'published',
            ]
    list_filter = [
            u'submission_date',
            simple_list_filter_factory(u'Undecided E-mail', u'undecided', [
                (u'1', u'With', lambda qs: qs.filter(undecided_emails_count__gt=0)),
                (u'0', u'Without', lambda qs: qs.filter(undecided_emails_count=0)),
                ]),
            u'closed',
            u'published',
            ]
    search_fields = [
            u'=id',
            u'applicant__first_name',
            u'applicant__last_name',
            u'applicant__email',
            u'branch__obligee__name',
            u'unique_email',
            u'subject',
            ]
    ordering = [
            u'-submission_date',
            u'-id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'applicant',
            ]
    inlines = [
            BranchInline,
            ]

    def get_queryset(self, request):
        queryset = super(InforequestAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'applicant')
        queryset = queryset.select_undecided_emails_count()
        queryset = queryset.prefetch_related(
                Inforequest.prefetch_main_branch(None, Branch.objects.select_related(u'obligee')))
        return queryset

@admin.register(InforequestDraft, site=admin.site)
class InforequestDraftAdmin(admin.ModelAdmin):
    date_hierarchy = u'modified'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.applicant,
                    u'{obj.first_name} {obj.last_name} <{obj.email}>'),
                short_description=u'Applicant',
                admin_order_field=u'applicant__email',
                ),
            decorate(
                lambda o: admin_obj_format(o.obligee, u'{obj.name}'),
                short_description=u'Obligee',
                admin_order_field=u'obligee',
                ),
            u'modified',
            ]
    list_filter = [
            u'modified',
            ]
    search_fields = [
            u'=id',
            u'applicant__first_name',
            u'applicant__last_name',
            u'applicant__email',
            u'obligee__name',
            ]
    ordering = [
            u'id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'applicant',
            u'obligee',
            ]
    inlines = [
            ]

    def get_queryset(self, request):
        queryset = super(InforequestDraftAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'applicant')
        queryset = queryset.select_related(u'obligee')
        return queryset

@admin.register(InforequestEmail, site=admin.site)
class InforequestEmailAdmin(admin.ModelAdmin):
    date_hierarchy = None
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.inforequest),
                short_description=u'Inforequest',
                admin_order_field=u'inforequest',
                ),
            decorate(
                lambda o: admin_obj_format(o.email),
                short_description=u'E-mail',
                admin_order_field=u'email',
                ),
            u'type',
            ]
    list_filter = [
            u'type',
            ]
    search_fields = [
            u'=id',
            u'=inforequest__id',
            u'=email__id',
            ]
    ordering = [
            u'id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'inforequest',
            u'email',
            ]
    inlines = [
            ]

    def get_queryset(self, request):
        queryset = super(InforequestEmailAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'inforequest')
        queryset = queryset.select_related(u'email')
        return queryset

class ActionInline(ReadOnlyAdminInlineMixin, admin.TabularInline):
    model = Action
    fields = [
            decorate(
                lambda o: admin_obj_format(o, u'{obj.pk}'),
                short_description=u'id',
                ),
            decorate(
                lambda o: admin_obj_format(o.email, u'{obj}'),
                short_description=u'E-mail',
                ),
            u'type',
            u'created',
            ]
    ordering = [
            u'-created',
            u'-id',
            ]

@admin.register(Branch, site=admin.site)
class BranchAdmin(admin.ModelAdmin):
    date_hierarchy = None
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.inforequest),
                short_description=u'Inforequest',
                admin_order_field=u'inforequest',
                ),
            decorate(
                lambda o: admin_obj_format(o.obligee, u'{obj.name}'),
                short_description=u'Obligee',
                admin_order_field=u'obligee',
                ),
            decorate(
                lambda o: admin_obj_format(o.advanced_by),
                short_description=u'Advanced by',
                admin_order_field=u'advanced_by',
                ),
            ]
    list_filter = [
            simple_list_filter_factory(u'Advanced', u'advanced', [
                (u'1', u'Yes', lambda qs: qs.advanced()),
                (u'2', u'No',  lambda qs: qs.main()),
                ]),
            ]
    search_fields = [
            u'=id',
            u'=inforequest__id',
            u'obligee__name',
            u'=advanced_by__id',
            ]
    ordering = [
            u'id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'inforequest',
            u'obligee',
            u'historicalobligee',
            u'advanced_by',
            ]
    inlines = [
            ActionInline,
            ]

    def get_queryset(self, request):
        queryset = super(BranchAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'inforequest')
        queryset = queryset.select_related(u'obligee')
        queryset = queryset.select_related(u'advanced_by')
        return queryset

@admin.register(Action, site=admin.site)
class ActionAdmin(admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.branch),
                short_description=u'Branch',
                admin_order_field=u'branch',
                ),
            decorate(
                lambda o: admin_obj_format(o.email),
                short_description=u'E-mail',
                admin_order_field=u'email',
                ),
            u'type',
            u'created',
            ]
    list_filter = [
            u'type',
            u'created',
            ]
    search_fields = [
            u'=id',
            u'=branch__id',
            u'=email__id',
            ]
    ordering = [
            u'-created',
            u'-id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'branch',
            u'email',
            ]
    inlines = [
            BranchInline,
            ]

    def get_queryset(self, request):
        queryset = super(ActionAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'branch')
        queryset = queryset.select_related(u'email')
        return queryset
