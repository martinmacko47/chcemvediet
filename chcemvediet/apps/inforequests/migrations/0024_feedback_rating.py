# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inforequests', '0023_auto_20231201_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='rating',
            field=models.SmallIntegerField(default=None, blank=True, choices=[(0, 'Stra\u0161n\xfd'), (1, 'Ve\u013emi zl\xfd'), (2, 'Zl\xfd'), (3, 'Priemern\xfd'), (4, 'Dobr\xfd'), (5, 'Ve\u013emi dobr\xfd'), (6, 'Vynikaj\xfaci'), (7, 'Mimoriadny')]),
            preserve_default=True,
        ),
    ]
