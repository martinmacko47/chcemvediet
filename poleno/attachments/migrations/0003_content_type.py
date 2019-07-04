# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import magic

from django.db import models, migrations

def forward(apps, schema_editor):
    Attachment = apps.get_model(u'attachments', u'Attachment')
    mime = magic.Magic(mime=True)
    for attachment in Attachment.objects.all():
        content_type = mime.from_buffer(attachment.file.read())
        attachment.content_type = content_type
        attachment.save()

def backward(apps, schema_editor):
    # No need to encode names back.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0002_name_encoding'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]