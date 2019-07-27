import os
import shutil
import traceback
import tempfile

import subprocess32
from django.core.files.base import ContentFile
from wand.image import Image
from wand.resource import limits
import wand

from poleno.cron import cron_job, cron_logger
from poleno.attachments.models import Attachment
from poleno.utils.misc import guess_extension
from chcemvediet.apps.inforequests.models import Action

from .models import AttachmentNormalization
from .utils import temporary_directory
from . import content_types


LIBREOFFICE_TIMEOUT = 300

def normalize_pdf(attachment):
    AttachmentNormalization.objects.create(
        attachment=attachment,
        successful=True,
        file=ContentFile(attachment.content),
        content_type=content_types.PDF_CONTENT_TYPE
    )
    cron_logger.info(u'Normalized attachment: {}'.format(attachment))

def normalize_using_libreoffice(attachment):
    try:
        p = None
        with temporary_directory() as directory_name:
            filename = os.path.join(directory_name, u'file' + guess_extension(attachment.content_type))
            shutil.copy2(attachment.file.path, filename)
            p = subprocess32.run(
                [u'libreoffice', u'--headless', u'--convert-to', u'pdf', u'--outdir', directory_name,
                 filename],
                stdout=subprocess32.PIPE,
                stderr=subprocess32.PIPE,
                timeout=LIBREOFFICE_TIMEOUT
            )
            with open(os.path.join(directory_name, u'file.pdf'), u'rb') as file_pdf:
                AttachmentNormalization.objects.create(
                    attachment=attachment,
                    successful=True,
                    file=ContentFile(file_pdf.read()),
                    content_type=content_types.PDF_CONTENT_TYPE,
                    debug=u'STDOUT:\n{}\nSTDERR:\n{}'.format(p.stdout, p.stderr)
                )
            cron_logger.info(u'Normalized attachment using libreoffice: {}'.format(attachment))
    except Exception as e:
        trace = unicode(traceback.format_exc(), u'utf-8')
        stdout = p.stdout if p else getattr(e, u'stdout', u'')
        stderr = p.stderr if p else getattr(e, u'stderr', u'')
        AttachmentNormalization.objects.create(
            attachment=attachment,
            successful=False,
            content_type=content_types.PDF_CONTENT_TYPE,
            debug=u'STDOUT:\n{}\nSTDERR:\n{}\n{}'.format(stdout, stderr, trace)
        )
        cron_logger.error(u'Normalizing attachment using libreoffice has failed: {}\n An '
                          u'unexpected error occured: {}\n{}'.format(
                                  attachment, e.__class__.__name__, trace))

def normalize_using_imagemagic(attachment):
    try:
        with Image(filename=attachment.file.path) as original:
            with original.convert(u'pdf') as converted:
                AttachmentNormalization.objects.create(
                    attachment=attachment,
                    successful=True,
                    file=ContentFile(converted.make_blob()),
                    content_type=content_types.PDF_CONTENT_TYPE,
                )
        cron_logger.info(u'Normalized attachment using imagemagic: {}'.format(attachment))
    except Exception as e:
        trace = unicode(traceback.format_exc(), u'utf-8')
        AttachmentNormalization.objects.create(
            attachment=attachment,
            successful=False,
            content_type=content_types.PDF_CONTENT_TYPE,
            debug=u'{}'.format(trace)
        )
        cron_logger.error(u'Normalizing attachment using imagemagic has failed: {}\n An '
                          u'unexpected error occured: {}\n{}'.format(
                                  attachment, e.__class__.__name__, trace))

def skip_normalization(attachment):
    AttachmentNormalization.objects.create(
        attachment=attachment,
        successful=False,
        content_type=None,
        debug=u'Not supported content type'
    )
    cron_logger.info(u'Skipping normalization of attachment with not supported content '
                     u'type: {}'.format(attachment))

@cron_job(run_every_mins=1)
def attachment_normalization():
    attachment = (Attachment.objects.attached_to(Action)
            .filter(attachmentnormalization__isnull=True)
            .first()
            )
    if attachment is None:
        return
    elif attachment.content_type == content_types.PDF_CONTENT_TYPE:
        normalize_pdf(attachment)
    elif attachment.content_type in content_types.LIBREOFFICE_CONTENT_TYPES:
        normalize_using_libreoffice(attachment)
    elif attachment.content_type in content_types.IMAGEMAGICK_CONTENT_TYPES:
        normalize_using_imagemagic(attachment)
    else:
        skip_normalization(attachment)
