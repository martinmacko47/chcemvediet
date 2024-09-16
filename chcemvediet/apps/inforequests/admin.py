# vim: expandtab
# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.db import router, transaction
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from poleno.utils.date import local_today
from poleno.utils.misc import decorate, squeeze
from poleno.utils.admin import (simple_list_filter_factory, admin_obj_format,
                                ReadOnlyAdminInlineMixin, BulkDeleteAdminMixin)
from chcemvediet.apps.inforequests.constants import ADMIN_EXTEND_SNOOZE_BY_DAYS

from .models import Inforequest, InforequestDraft, InforequestEmail, Branch, Action, Feedback


class DeleteNestedInforequestEmailAdminMixin(BulkDeleteAdminMixin, admin.ModelAdmin):

    def nested_inforequestemail_queryset(self, objs):
        using = router.db_for_write(self.model)
        collector = NestedObjects(using)
        collector.collect(objs)
        to_delete = collector.nested()
        actions = [obj for obj in self.nested_objects_traverse(to_delete)
                   if isinstance(obj, Action)]
        inforequestemails_qs = InforequestEmail.objects.none()
        for action in actions:
            if action.email:
                inforequestemails_qs |= InforequestEmail.objects.filter(
                        inforequest=action.branch.inforequest,
                        email=action.email,
                )
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
        outbound, inbound = self.nested_inforequestemail_queryset([context[u'object']])
        context[u'outbound'] = [admin_obj_format(inforequestemail) for inforequestemail in outbound]
        context[u'inbound'] = [admin_obj_format(inforequestemail) for inforequestemail in inbound]
        return super(DeleteNestedInforequestEmailAdminMixin, self).render_delete_form(request,
                                                                                      context)

    @transaction.atomic
    def delete_selected(self, request, queryset):
        outbound, inbound = self.nested_inforequestemail_queryset(queryset)
        template_response = super(DeleteNestedInforequestEmailAdminMixin, self).delete_selected(request, queryset)

        if request.POST.get(u'post'):
            outbound.delete()
            inbound.update(type=InforequestEmail.TYPES.UNDECIDED)
            return None

        template_response.context_data.update({
            u'outbound': [admin_obj_format(inforequestemail) for inforequestemail in outbound],
            u'inbound': [admin_obj_format(inforequestemail) for inforequestemail in inbound],
        })
        return template_response

    def delete_model(self, request, obj):
        outbound, inbound = self.nested_inforequestemail_queryset([obj])
        super(DeleteNestedInforequestEmailAdminMixin, self).delete_model(request, obj)
        outbound.delete()
        inbound.update(type=InforequestEmail.TYPES.UNDECIDED)

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
    actions = [
            u'delete_selected',
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
    actions = [
            u'delete_selected',
    ]

    def get_queryset(self, request):
        queryset = super(InforequestDraftAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'applicant')
        queryset = queryset.select_related(u'obligee')
        return queryset

@admin.register(InforequestEmail, site=admin.site)
class InforequestEmailAdmin(BulkDeleteAdminMixin, admin.ModelAdmin):
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

    def delete_constraints(self, objs):
        constraints = []
        for obj in objs:
            actions = Action.objects.of_inforequest(obj.inforequest).filter(email=obj.email)
            if actions:
                constraints.append(format_html(
                    u'{} is used for {}.'.format(
                            admin_obj_format(obj),
                            u', '.join([admin_obj_format(action) for action in actions]),
                    )))
        return constraints

@admin.register(Branch, site=admin.site)
class BranchAdmin(DeleteNestedInforequestEmailAdminMixin, admin.ModelAdmin):
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

    def delete_constraints(self, objs):
        constraints = []
        for obj in objs:
            if obj.is_main:
                constraints.append(format_html(u'{} is main.'.format(admin_obj_format(obj))))
        return constraints

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

    def get_queryset(self, request):
        queryset = super(ActionAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'branch')
        queryset = queryset.select_related(u'email')
        return queryset

    def delete_warnings(self, objs):
        warnings = []
        for obj in objs:
            if not obj.is_last_action and obj.next_action not in objs:
                warnings.append(format_html(squeeze(u"""
                        {} is not the last action in the branch. Deleting it may cause logical
                        errors in the inforequest history.
                        """).format(admin_obj_format(obj))))
        return warnings

    def delete_constraints(self, objs):
        constraints = []
        for obj in objs:
            if obj.type in [Action.TYPES.REQUEST, Action.TYPES.ADVANCED_REQUEST]:
                constraints.append(format_html(
                    u'{} is type {}.'.format(admin_obj_format(obj), obj.get_type_display())))
            if len(obj.branch.actions) == 1:
                constraints.append(format_html(
                    u'{} is the only action in the branch.'.format(admin_obj_format(obj))))
        return constraints

    def can_snooze_previous_action(self, obj):
        if obj.type not in [Action.TYPES.EXPIRATION, Action.TYPES.APPEAL_EXPIRATION]:
            return False
        if not obj.previous_action:
            return False
        return True

    def snooze_action(self, obj):
        obj.snooze = local_today() + datetime.timedelta(days=ADMIN_EXTEND_SNOOZE_BY_DAYS)
        obj.save(update_fields=[u'snooze'])

    def render_delete_form(self, request, context):
        obj = context[u'object']
        if self.can_snooze_previous_action(obj):
            context[u'snoozed_actions'] = [admin_obj_format(obj.previous_action)]
            context[u'ADMIN_EXTEND_SNOOZE_BY_DAYS'] = ADMIN_EXTEND_SNOOZE_BY_DAYS
        return super(ActionAdmin, self).render_delete_form(request, context)

    @transaction.atomic
    def delete_selected(self, request, queryset):
        snoozed_actions = []
        for obj in queryset:
            if self.can_snooze_previous_action(obj) and obj.previous_action not in queryset:
                snoozed_actions.append(obj.previous_action)

        template_response = super(ActionAdmin, self).delete_selected(request, queryset)

        if request.POST.get(u'post'):
            if request.POST.get(u'snooze'):
                for action in snoozed_actions:
                    self.snooze_action(action)
            return None

        template_response.context_data.update({
                u'snoozed_actions': [admin_obj_format(action) for action in snoozed_actions],
                u'ADMIN_EXTEND_SNOOZE_BY_DAYS': ADMIN_EXTEND_SNOOZE_BY_DAYS,
        })
        return template_response

    def delete_model(self, request, obj):
        super(ActionAdmin, self).delete_model(request, obj)
        if request.POST.get(u'snooze') and self.can_snooze_previous_action(obj):
            self.snooze_action(obj.previous_action)


@admin.register(Feedback, site=admin.site)
class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = u'created'
    list_display = [
        u'id',
        decorate(
            lambda o: admin_obj_format(o.inforequest),
            short_description=u'Inforequest',
            admin_order_field=u'inforequest'
        ),
        u'created',
        u'content',
        u'rating'
    ]
    list_filter = [
        u'created',
        u'rating'
    ]
    ordering = [
        u'-created',
        u'-id',
        u'inforequest__id'
    ]
    exclude = [
    ]
    readonly_fields = [
        u'inforequest',
        u'content',
        u'created',
        u'rating'
    ]
    raw_id_fields = [
        u'inforequest'
    ]


