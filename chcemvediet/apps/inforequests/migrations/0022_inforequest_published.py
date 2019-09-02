# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inforequests', '0021_auto_20151213_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='inforequest',
            name='published',
            field=models.BooleanField(default=False, help_text='True if the inforequest is published and everybody can see it. Non-published inforequests can be seen only by the user who created them.'),
            preserve_default=True,
        ),
    ]
