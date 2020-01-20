# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='anonymized_inforequest',
            field=models.BooleanField(default=True, help_text='If true, published inforequests will be shown anonymized, otherwise in their original version.'),
            preserve_default=True,
        ),
    ]
