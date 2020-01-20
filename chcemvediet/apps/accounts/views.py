# vim: expandtab
# -*- coding: utf-8 -*-
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
@login_required
def settings(request):
    if request.method == u'POST':
        form = SettingsForm(request.user, request.POST)
        if form.is_valid():
            profile = request.user.profile
            profile.anonymized_inforequest = form.cleaned_data[u'anonymized_inforequest']
            profile.save(update_fields=[u'anonymized_inforequest'])
            return HttpResponseRedirect(reverse(u'accounts:settings'))
    else:
        form = SettingsForm(request.user)
    return render(request, u'accounts/settings.html', {u'form': form})
