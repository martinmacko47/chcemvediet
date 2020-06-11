# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


SITE_ID = 1

def forward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    SocialAccount = apps.get_model(u'socialaccount', u'SocialAccount')
    SocialApp.objects.filter(provider__in=[u'twitter', u'linkedin']).delete()
    SocialAccount.objects.filter(provider__in=[u'twitter', u'linkedin']).delete()

def backward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    twitter = SocialApp.objects.create(provider=u'twitter', name=u'Twitter OAuth')
    twitter.sites.add(SITE_ID)
    linkedin = SocialApp.objects.create(provider=u'linkedin', name=u'Linkedin OAuth')
    linkedin.sites.add(SITE_ID)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_days_to_publish_inforequest'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
