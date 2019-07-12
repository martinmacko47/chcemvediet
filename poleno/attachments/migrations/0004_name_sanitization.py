# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mimetypes
import os

from django.db import models, migrations

from poleno.utils.misc import guess_extension


def forward(apps, schema_editor):
    Attachment = apps.get_model(u'attachments', u'Attachment')
    for attachment in Attachment.objects.all():
        base, extension = os.path.splitext(attachment.name)
        base = ''.join([c for c in base if not ord(c) < 32][:200])
        if mimetypes.guess_type(attachment.name)[0] != attachment.content_type:
            extension = guess_extension(attachment.content_type)
        name = (base or u'attachment') + extension
        if attachment.name != name:
            attachment.name = name
            attachment.save()

def backward(apps, schema_editor):
    # No need to change name back to untrusted
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0003_content_type_sanitization'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
        migrations.AlterField(
            model_name='attachment',
            name='name',
            field=models.CharField(
                help_text='Attachment file name, e.g. "document.pdf". Automatically sanitized when creating a new object.',
                max_length=255),
            preserve_default=True,
        ),
    ]
