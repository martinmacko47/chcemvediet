# vim: expandtab
# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from poleno.utils.date import local_today
from poleno.utils.misc import decorate, squeeze
from poleno.utils.admin import (simple_list_filter_factory, admin_obj_format,
                                ReadOnlyAdminInlineMixin, NoBulkDeleteAdminMixin)

from .models import Inforequest, InforequestDraft, InforequestEmail, Branch, Action


class DeleteNestedInforequestEmailAdminMixin(admin.ModelAdmin):

    def get_inforequest(self, obj):
        raise NotImplementedError

    def nested_inforequestemail_queryset(self, obj):
        using = router.db_for_write(self.model)
        collector = NestedObjects(using)
        collector.collect([obj])
        to_delete = collector.nested()
        inforequest = self.get_inforequest(obj)
        actions = [obj for obj in self.nested_objects_traverse(to_delete)
                   if isinstance(obj, Action)]
        emails = [action.email for action in actions if action.email]
        inforequestemails_qs = InforequestEmail.objects.filter(inforequest=inforequest,
                                                               email__in=emails)
        outbound = inforequestemails_qs.filter(type=InforequestEmail.TYPES.APPLICANT_ACTION)
        inbound = inforequestemails_qs.filter(type=InforequestEmail.TYPES.OBLIGEE_ACTION)
        return outbound, inbound

    def nested_objects_traverse(self, to_delete):
        try:
            for obj in iter(to_delete):
                for nested_obj in self.nested_objects_traverse(obj):
                    yield nested_obj
        except TypeError:
            yield to_delete

    def render_delete_form(self, request, context):
        obj = context[u'object']
        outbound, inbound = self.nested_inforequestemail_queryset(obj)
        if outbound:
            context[u'deleted_objects'].extend([
                u'Outbound messages will be deleted:',
                [admin_obj_format(inforequestemail) for inforequestemail in outbound]
            ])
        if inbound:
            context[u'deleted_objects'].extend([
                u'Inbound messages will be marked undecided:',
                [admin_obj_format(inforequestemail) for inforequestemail in inbound]
            ])
        return super(DeleteNestedInforequestEmailAdminMixin, self).render_delete_form(request,
                                                                                      context)

    def delete_model(self, request, obj):
        outbound, inbound = self.nested_inforequestemail_queryset(obj)
        outbound.delete()
        inbound.update(type=InforequestEmail.TYPES.UNDECIDED)
        super(DeleteNestedInforequestEmailAdminMixin, self).delete_model(request, obj)

class BranchFormSet(BaseInlineFormSet):
    def get_queryset(self):
        qs = super(BranchFormSet, self).get_queryset()
        return sorted(qs, key=lambda branch: branch.tree_order)

class BranchInline(ReadOnlyAdminInlineMixin, admin.TabularInline):
    model = Branch
    formset = BranchFormSet
    fields = [
            decorate(
                lambda o: format_html(u'{} {}', u'—' * (len(o.tree_order) - 1),
                                      admin_obj_format(o)),
                short_description=u'id',
                ),
            decorate(
                lambda o: admin_obj_format(o.obligee, u'{obj.name}'),
                short_description=u'obligee',
                ),
            ]

class ActionInline(ReadOnlyAdminInlineMixin, admin.TabularInline):
    model = Action
    fields = [
            decorate(
                lambda o: admin_obj_format(o),
                short_description=u'id',
                ),
            decorate(
                lambda o: admin_obj_format(o.email),
                short_description=u'E-mail',
                ),
            u'type',
            u'created',
            ]
    ordering = [
            u'-created',
            u'-id',
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

@admin.register(Branch, site=admin.site)
class BranchAdmin(NoBulkDeleteAdminMixin, DeleteNestedInforequestEmailAdminMixin, admin.ModelAdmin):
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

    def get_inforequest(self, obj):
        return obj.inforequest

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return not obj.is_main

@admin.register(Action, site=admin.site)
class ActionAdmin(NoBulkDeleteAdminMixin, DeleteNestedInforequestEmailAdminMixin, admin.ModelAdmin):
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
    delete_confirmation_template = u'inforequests/admin/action_delete_confirmation.html'

    def get_queryset(self, request):
        queryset = super(ActionAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'branch')
        queryset = queryset.select_related(u'email')
        return queryset

    def get_inforequest(self, obj):
        return obj.branch.inforequest

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        if obj.type in [Action.TYPES.REQUEST, Action.TYPES.ADVANCED_REQUEST]:
            return False
        if len(obj.branch.actions) > 1:
            return True
        return False

    def render_delete_form(self, request, context):
        action = context[u'object']
        if not action.is_last_action:
            context[u'deleted_objects'].insert(0, format_html(squeeze(u"""
                <b>Warning:</b> The deleted action is not the last action in the branch. Deleting it
                may cause logical errors in the inforequest history.
                """)))
        return super(ActionAdmin, self).render_delete_form(request, context)

    def delete_model(self, request, obj):
        if request.POST:
            if request.POST.get(u'snooze'):
                previous = obj.previous_action
                previous.snooze = local_today() + datetime.timedelta(days=7)
                previous.save(update_fields=[u'snooze'])
        return super(ActionAdmin, self).delete_model(request, obj)
