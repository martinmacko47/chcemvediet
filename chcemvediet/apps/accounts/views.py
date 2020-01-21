# vim: expandtab
# -*- coding: utf-8 -*-
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from poleno.utils.urls import reverse

from .forms import SettingsForm


@require_http_methods([u'HEAD', u'GET'])
@login_required
def profile(request):
    return render(request, u'accounts/profile.html')

@require_http_methods([u'HEAD', u'GET', u'POST'])
@transaction.atomic
@login_required
def settings(request):
    if request.method == u'POST':
        form = SettingsForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(u'accounts:settings'))
    else:
        form = SettingsForm(
                request.user,
                initial={u'anonymize_inforequests': request.user.profile.anonymize_inforequests}
                )
    return render(request, u'accounts/settings.html', {u'form': form})
