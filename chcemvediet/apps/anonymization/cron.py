import os
import shutil
import tempfile
import traceback

import subprocess32
from django.core.files.base import ContentFile

from poleno.cron import cron_job, cron_logger
from poleno.attachments.models import Attachment
from poleno.utils.misc import guess_extension
from chcemvediet.apps.inforequests.models import Action

from .models import AttachmentNormalization
from . import content_types


@cron_job(run_every_mins=1)
def attachment_normalization():
    attachment = (Attachment.objects.attached_to(Action)
            .filter(attachmentnormalization__isnull=True)
            .first()
            )

    if attachment is None:
        return

    if attachment.content_type == content_types.PDF_CONTENT_TYPE:
        AttachmentNormalization.objects.create(
            attachment=attachment,
            successful=True,
            file=ContentFile(attachment.content),
            content_type=content_types.PDF_CONTENT_TYPE
        )
        cron_logger.info(u'Normalized attachment: {}'.format(attachment))

    elif attachment.content_type in content_types.LIBREOFFICE_CONTENT_TYPES:
        directory_name = tempfile.mkdtemp(dir=u'.')
        file_copy = os.path.join(directory_name, u'file' + guess_extension(attachment.content_type))
        shutil.copy2(attachment.file.path, file_copy)

        p = subprocess32.Popen(
            [u'libreoffice', u'--headless', u'--convert-to', u'pdf', u'--outdir', directory_name,
             file_copy],
            stdout=subprocess32.PIPE,
            stderr=subprocess32.PIPE
        )
        try:
            out, err = p.communicate(timeout=300)
        except subprocess32.TimeoutExpired:
            p.terminate()
            out, err = p.communicate()
            err += u'Timeout expired.'

        if u'file.pdf' in os.listdir(directory_name):
            file_pdf = open(os.path.join(directory_name, u'file.pdf'), u'rb')
            AttachmentNormalization.objects.create(
                attachment=attachment,
                successful=True,
                file=ContentFile(file_pdf.read()),
                content_type=content_types.PDF_CONTENT_TYPE,
                debug=u'{}\n{}'.format(out, err)
            )
            cron_logger.info(u'Normalized attachment using libreoffice: {}'.format(attachment))
        else:
            AttachmentNormalization.objects.create(
                attachment=attachment,
                successful=False,
                content_type=content_types.PDF_CONTENT_TYPE,
                debug=u'{}\n{}'.format(out, err)
            )
            trace = unicode(traceback.format_exc(), u'utf-8')
            cron_logger.info(u'Normalizing attachment using libreoffice has failed: {}\n{}'
                             .format(attachment, trace))
        shutil.rmtree(directory_name)

    else:
        AttachmentNormalization.objects.create(
            attachment=attachment,
            successful=False,
            content_type=None,
            debug=u'Not supported content type'
        )
        cron_logger.info(u'Skipping normalization of attachment with not supported content '
                         u'type: {}'.format(attachment))
