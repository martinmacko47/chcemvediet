# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import magic
from django.db import models, migrations


def forward(apps, schema_editor):
    Attachment = apps.get_model(u'attachments', u'Attachment')
    for attachment in Attachment.objects.all():
        try:
            content_type = magic.from_buffer(attachment.file.read(), mime=True)
        finally:
            attachment.file.close()
        if attachment.content_type != content_type:
            attachment.content_type = content_type
            attachment.save()

def backward(apps, schema_editor):
    # No need to change content_type back to untrusted
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0002_name_encoding'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
        migrations.AlterField(
            model_name='attachment',
            name='content_type',
            field=models.CharField(help_text='Attachment content type, e.g. "application/pdf". Automatically computed when creating a new object.', max_length=255),
            preserve_default=True,
        ),
    ]
