# vim: expandtab
# -*- coding: utf-8 -*-
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponseRedirect

from poleno.utils.urls import reverse
from poleno.utils.views import require_ajax, login_required
from chcemvediet.apps.wizards.views import wizard_view
from chcemvediet.apps.inforequests.forms import FeedbackActionWizard
from chcemvediet.apps.inforequests.forms import SnoozeForm
from chcemvediet.apps.inforequests.forms import AppealWizard, ClarificationResponseWizard
from chcemvediet.apps.inforequests.forms import ObligeeActionWizard
from chcemvediet.apps.inforequests.models import Inforequest, Action

from .shortcuts import render_form, json_form, json_success


@require_http_methods([u'HEAD', u'GET', u'POST'])
@transaction.atomic
@login_required(raise_exception=True)
def feedback_action(request, inforequest_slug, inforequest_pk, step_idx=None):
    inforequest = (Inforequest.objects
                   .not_closed().owned_by(request.user).get_or_404(pk=inforequest_pk))

    if inforequest_slug != inforequest.slug:
        return HttpResponseRedirect(reverse(u'inforequests:feedback_action',
                                            kwargs=dict(inforequest=inforequest, step_idx=step_idx)))

    return wizard_view(FeedbackActionWizard, request, step_idx, inforequest)


@require_http_methods([u'HEAD', u'GET', u'POST'])
@transaction.atomic
@login_required(raise_exception=True)
def obligee_action(request, inforequest_slug, inforequest_pk, step_idx=None):
    inforequest = (Inforequest.objects
            .not_closed().owned_by(request.user).get_or_404(pk=inforequest_pk))
    inforequestemail = inforequest.inforequestemail_set.undecided().oldest().get_or_none()
    email = inforequestemail.email if inforequestemail is not None else None

    if inforequest_slug != inforequest.slug:
        return HttpResponseRedirect(reverse(u'inforequests:obligee_action',
                kwargs=dict(inforequest=inforequest, step_idx=step_idx)))

    return wizard_view(ObligeeActionWizard, request, step_idx,
            inforequest, inforequestemail, email)

@require_http_methods([u'HEAD', u'GET', u'POST'])
@transaction.atomic
@login_required(raise_exception=True)
def clarification_response(request, inforequest_slug, inforequest_pk, branch_pk, step_idx=None):
    inforequest = (Inforequest.objects
            .not_closed().owned_by(request.user).get_or_404(pk=inforequest_pk))
    branch = inforequest.branch_set.get_or_404(pk=branch_pk)

    if not branch.can_add_clarification_response:
        raise Http404()
    if inforequest_slug != inforequest.slug:
        return HttpResponseRedirect(reverse(u'inforequests:clarification_response',
                kwargs=dict(branch=branch, step_idx=step_idx)))

    return wizard_view(ClarificationResponseWizard, request, step_idx, branch)

@require_http_methods([u'HEAD', u'GET', u'POST'])
@transaction.atomic
@login_required(raise_exception=True)
def appeal(request, inforequest_slug, inforequest_pk, branch_pk, step_idx=None):
    inforequest = (Inforequest.objects
            .not_closed().owned_by(request.user).get_or_404(pk=inforequest_pk))
    branch = inforequest.branch_set.get_or_404(pk=branch_pk)

    if not branch.can_add_appeal:
        raise Http404()
    if inforequest_slug != inforequest.slug:
        return HttpResponseRedirect(reverse(u'inforequests:appeal',
                kwargs=dict(branch=branch, step_idx=step_idx)))

    return wizard_view(AppealWizard, request, step_idx, branch)

@require_http_methods([u'HEAD', u'GET', u'POST'])
@require_ajax
@transaction.atomic
@login_required(raise_exception=True)
def snooze(request, inforequest_slug, inforequest_pk, branch_pk, action_pk):
    inforequest = (Inforequest.objects
            .not_closed().owned_by(request.user).get_or_404(pk=inforequest_pk))
    branch = inforequest.branch_set.get_or_404(pk=branch_pk)
    action = branch.last_action

    if action.pk != Action._meta.pk.to_python(action_pk):
        raise Http404()
    if not action.can_applicant_snooze:
        raise Http404()
    if inforequest.has_undecided_emails:
        raise Http404()
    if inforequest_slug != inforequest.slug:
        return HttpResponseRedirect(reverse(u'inforequests:snooze', kwargs=dict(action=action)))

    if request.method != u'POST':
        form = SnoozeForm(prefix=action.pk)
        return render_form(request, form, inforequest=inforequest, branch=branch, action=action)

    form = SnoozeForm(request.POST, prefix=action.pk)
    if not form.is_valid():
        return json_form(request, form, inforequest=inforequest, branch=branch, action=action)

    form.save(action)
    action.save(update_fields=[u'snooze'])

    # The inforequest was changed, we need to refetch it
    inforequest = Inforequest.objects.prefetch_detail().get(pk=inforequest.pk)
    return json_success(request, inforequest)
