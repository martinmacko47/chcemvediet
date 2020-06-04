# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def forward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    SocialApp.objects.filter(pk__in=[3, 4]).delete()

def backward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    twitter = SocialApp.objects.create(pk=3, provider=u'twitter', name=u'Twitter OAuth')
    twitter.sites.add(1)
    linkedin = SocialApp.objects.create(pk=4, provider=u'linkedin', name=u'Linkedin OAuth')
    linkedin.sites.add(1)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_days_to_publish_inforequest'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
