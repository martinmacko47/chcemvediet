# vim: expandtab
# -*- coding: utf-8 -*-
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib.auth.models import User

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

@require_http_methods([u'HEAD', u'GET'])
def search(request):
    q = request.GET.get(u'q', u'')

    return render(request, u'main/search/search.html', {
        u'q': q,
    })
