# vim: expandtab
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from poleno.utils.lazy import lazy_format

from . import views


urlpatterns = patterns(u'',
    url(r'^profile/$', views.profile, name=u'profile'),
    url(lazy_format(r'^{0}/',  _(u'accounts:urls:settings')), views.settings, name=u'settings'),
)
