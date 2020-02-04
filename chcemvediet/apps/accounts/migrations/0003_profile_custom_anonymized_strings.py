# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_anonymize_inforequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='custom_anonymized_strings',
            field=jsonfield.fields.JSONField(default=None, help_text='User defined strings for anonymization. NULL for default anonymization.', null=True),
            preserve_default=True,
        ),
    ]
