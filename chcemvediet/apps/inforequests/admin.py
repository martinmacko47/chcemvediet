# vim: expandtab
# -*- coding: utf-8 -*-
import datetime

from django.contrib.admin.actions import delete_selected
from django.contrib import admin, messages
from django.contrib.admin.utils import NestedObjects
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from poleno.utils.date import local_today
from poleno.utils.misc import decorate, squeeze
from poleno.utils.admin import (simple_list_filter_factory, admin_obj_format,
                                ReadOnlyAdminInlineMixin, NoBulkDeleteAdminMixin)
from chcemvediet.apps.inforequests.constants import ADMIN_EXTEND_SNOOZE_BY_DAYS

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
        outbound, inbound = self.nested_inforequestemail_queryset(context[u'object'])
        context[u'outbound'] = [admin_obj_format(inforequestemail) for inforequestemail in outbound]
        context[u'inbound'] = [admin_obj_format(inforequestemail) for inforequestemail in inbound]
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

    def delete_constraints(self, obj):
        if obj.is_main:
            return [format_html(u'{} is main.'.format(admin_obj_format(obj)))]

    def render_delete_form(self, request, context):
        context[u'delete_constraints'] = self.delete_constraints(context[u'object'])
        return super(BranchAdmin, self).render_delete_form(request, context)

    def delete_model(self, request, obj):
        if self.delete_constraints(obj):
            raise PermissionDenied
        return super(BranchAdmin, self).delete_model(request, obj)

@admin.register(Action, site=admin.site)
class ActionAdmin(DeleteNestedInforequestEmailAdminMixin, admin.ModelAdmin):
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
    actions = [
            u'delete_selected'
    ]

    def get_queryset(self, request):
        queryset = super(ActionAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'branch')
        queryset = queryset.select_related(u'email')
        return queryset

    def get_inforequest(self, obj):
        return obj.branch.inforequest

    def delete_constraints(self, obj):
        constraints = []
        if obj.type in [Action.TYPES.REQUEST, Action.TYPES.ADVANCED_REQUEST]:
            constraints.append(format_html(
                u'{} is type {}.'.format(admin_obj_format(obj), obj.get_type_display())))
        if len(obj.branch.actions) == 1:
            constraints.append(format_html(
                u'{} is the only action in the branch.'.format(admin_obj_format(obj))))
        return constraints

    def render_delete_form(self, request, context):
        context[u'delete_constraints'] = self.delete_constraints(context[u'object'])
        context[u'ADMIN_EXTEND_SNOOZE_BY_DAYS'] = ADMIN_EXTEND_SNOOZE_BY_DAYS
        return super(ActionAdmin, self).render_delete_form(request, context)

    @transaction.atomic
    def delete_selected(self, request, queryset):
        constraints = []
        warnings = []
        outbound = InforequestEmail.objects.none()
        inbound = InforequestEmail.objects.none()
        for obj in queryset:
            obj_constraints = self.delete_constraints(obj)
            constraints += obj_constraints
            inforequestemails = self.nested_inforequestemail_queryset(obj)
            outbound |= inforequestemails[0]
            inbound |= inforequestemails[1]
            if not obj_constraints:
                if not obj.is_last_action and obj.next_action not in queryset:
                    warnings.append(format_html(squeeze(u"""
                            {} is not the last action in the branch. Deleting it may cause logical
                            errors in the inforequest history.
                            """).format(admin_obj_format(obj))))

        if request.POST.get(u'post'):
            if constraints:
                raise PermissionDenied

        template_response = delete_selected(self, request, queryset)

        if request.POST.get(u'post'):
            n = outbound.count()
            if n:
                outbound.delete()
                self.message_user(request,
                        u'Successfully deleted {} applicant_action inforequestemails.'.format(n),
                        messages.SUCCESS)
            m = inbound.count()
            if m:
                inbound.update(type=InforequestEmail.TYPES.UNDECIDED)
                self.message_user(request,
                        u'Successfully updated {} obligee_action inforequestemails.'.format(m),
                        messages.SUCCESS)
            return None

        template_response.context_data.update({
                u'outbound': [admin_obj_format(inforequestemail) for inforequestemail in outbound],
                u'inbound': [admin_obj_format(inforequestemail) for inforequestemail in inbound],
                u'delete_constraints': constraints,
                u'warnings': warnings,
        })
        return template_response
    delete_selected.short_description = u'Delete selected actions'

    def delete_model(self, request, obj):
        if self.delete_constraints(obj):
            raise PermissionDenied
        if request.POST:
            if (request.POST.get(u'snooze')
                    and obj.type in [Action.TYPES.EXPIRATION, Action.TYPES.APPEAL_EXPIRATION]
                    and obj.previous_action):
                previous = obj.previous_action
                previous.snooze = local_today() + datetime.timedelta(days=ADMIN_EXTEND_SNOOZE_BY_DAYS)
                previous.save(update_fields=[u'snooze'])
        return super(ActionAdmin, self).delete_model(request, obj)
