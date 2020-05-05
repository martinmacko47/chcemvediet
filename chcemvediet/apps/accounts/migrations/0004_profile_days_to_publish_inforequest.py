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
            name='days_to_publish_inforequest',
            field=models.IntegerField(default=60, help_text='User defined number of days after which inforequest can be marked as published, after closing inforequest.'),
            preserve_default=True,
        ),
    ]
