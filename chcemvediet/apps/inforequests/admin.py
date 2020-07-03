# vim: expandtab
# -*- coding: utf-8 -*-
import re

from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from poleno.utils.misc import decorate
from poleno.utils.admin import (simple_list_filter_factory, admin_obj_format,
                                ReadOnlyAdminInlineMixin)

from .models import Inforequest, InforequestDraft, InforequestEmail, Branch, Action


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

    def get_actions(self, request):
        actions = super(ActionAdmin, self).get_actions(request)
        if u'delete_selected' in actions:
            del actions[u'delete_selected']
        return actions

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
        context[u'deleted_objects'].extend(
            [format_inforequestemail(ire, request.user, self.admin_site) for ire in action.inforequestemails_to_delete])
        return super(ActionAdmin, self).render_delete_form(request, context)

    def delete_view(self, request, object_id, extra_context=None):
        from django.contrib.admin.utils import unquote
        if request.POST:  # The user has already confirmed the deletion.
            obj = self.get_object(request, unquote(object_id))
            for ire in obj.inforequestemails_to_delete.filter(type=InforequestEmail.TYPES.OBLIGEE_ACTION):
                pass
                # ire.type = int(request.POST['ire-{}'.format(ire.pk)])
                # ire.save()
        return super(ActionAdmin, self).delete_view(request, object_id, extra_context)

    def delete_model(self, request, obj):
        # obj.inforequestemails_to_delete.filter(type=InforequestEmail.TYPES.APPLICANT_ACTION).delete()
        super(ActionAdmin, self).delete_model(request, obj)

def format_inforequestemail(ire, user, admin_site):
    from django.utils.text import capfirst
    from django.core.urlresolvers import reverse, NoReverseMatch
    from django.contrib.admin.utils import quote
    from django.contrib.auth import get_permission_codename
    from poleno.utils.misc import squeeze
    from django.utils.encoding import force_text
    perms_needed = set()

    has_admin = ire.__class__ in admin_site._registry
    opts = ire._meta
    no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                               force_text(ire))
    if has_admin:
        try:
            admin_url = reverse('%s:%s_%s_change'
                                % (admin_site.name,
                                   opts.app_label,
                                   opts.model_name),
                                None, (quote(ire._get_pk_val()),))
        except NoReverseMatch:
            # Change url doesn't exist -- don't display link to edit
            return no_edit_link
        p = '%s.%s' % (opts.app_label,
                       get_permission_codename('delete', opts))
        if not user.has_perm(p):
            perms_needed.add(opts.verbose_name)
        # Display a link to the admin page.
        select_form = squeeze(u"""
                <div style="display:inline">
                <label class="required" for="ire-{4}"></label>
                <select id="ire-{4}" name="ire-{4}">
                <option value="3">Nerozhodnuté</option>
                <option value="4">Nesúvisiace</option>
                </select>
                </div>
                """
                )
        form = u'{0}: <a href="{1}">{2}</a> {3}'
        if ire.type == InforequestEmail.TYPES.OBLIGEE_ACTION:
            form += select_form
        return format_html(form,
                           capfirst(opts.verbose_name),
                           admin_url,
                           ire,
                           ire.get_type_display(),
                           ire.pk,
                           )
    else:
        # Don't display link to edit, because it either has no
        # admin or is edited inline.
        return no_edit_link
