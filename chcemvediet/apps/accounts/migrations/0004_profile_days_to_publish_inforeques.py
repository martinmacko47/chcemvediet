# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_custom_anonymized_strings'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='days_to_publish_inforequests',
            field=models.IntegerField(default=None, help_text='User defined number of days after which inforequest can be marked as published, after closing inforequest. NULL for default value DAYS_TO_PUBLISH_INFOREQUEST.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
