# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


SITE_ID = 1

def forward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    SocialAccount = apps.get_model(u'socialaccount', u'SocialAccount')
    SocialApp.objects.filter(provider=u'facebook').delete()
    SocialAccount.objects.filter(provider=u'facebook').delete()

def backward(apps, schema_editor):
    SocialApp = apps.get_model(u'socialaccount', u'SocialApp')
    facebook = SocialApp.objects.create(provider=u'facebook', name=u'Facebook OAuth')
    facebook.sites.add(SITE_ID)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_socialapp_remove_twitter_and_linkedin'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
