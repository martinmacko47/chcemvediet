# vim: expandtab
# -*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from chcemvediet.apps.obligees.models import Obligee
from chcemvediet.apps.inforequests.models import Inforequest


@require_http_methods([u'HEAD', u'GET'])
def homepage(request):
    users = User.objects.count()
    obligees = Obligee.objects.pending().count()
    inforequests = Inforequest.objects.count()

    return render(request, u'main/homepage/main.html', {
            u'users': users,
            u'obligees': obligees,
            u'inforequests': inforequests,
            })

@require_http_methods([u'HEAD', u'GET', u'POST'])
def customsearch(request):
    if request.POST:
        q = request.POST[u'q']
        return HttpResponseRedirect(reverse(u'customsearch') + u'?' + urlencode({u'q': q}))
    return render(request, u'customsearch/search.html')
