import os
import shutil
import traceback

import subprocess32
from django.core.files.base import ContentFile
from django.conf import settings

from poleno.cron import cron_logger
from poleno.utils.misc import guess_extension

from .utils import temporary_directory
from .models import AttachmentAnonymization
from . import content_types


LIBREOFFICE_TIMEOUT = 300

def anonymize_using_mock(attachment_anonymization):
    anonymized = os.path.join(settings.PROJECT_PATH,
                              u'chcemvediet/apps/anonymization/mocks/normalized.pdf')
    with open(anonymized, u'rb') as file:
        AttachmentAnonymization.objects.create(
            attachment=attachment_anonymization.attachment,
            successful=True,
            file=ContentFile(file.read()),
            content_type=content_types.PDF_CONTENT_TYPE,
            debug=u'Created using mocked libreoffice.'.format()
        )
    cron_logger.info(u'Anonymized attachment using mocked libreoffice: {}'.format(
        attachment_anonymization))

def anonymize_pdf(attachment_anonymization):
    if settings.MOCK_LIBREOFFICE:
        anonymize_using_mock(attachment_anonymization)
        return

    try:
        p = None
        with temporary_directory() as directory:
            filename = os.path.join(directory,
                                    u'file' + guess_extension(attachment_anonymization.content_type)
                                    )
            shutil.copy2(attachment_anonymization.file.path, filename)
            p = subprocess32.run(
                [u'libreoffice', u'--headless', u'--convert-to', u'pdf', u'--outdir', directory,
                 filename],
                stdout=subprocess32.PIPE,
                stderr=subprocess32.PIPE,
                timeout=LIBREOFFICE_TIMEOUT
            )
            with open(os.path.join(directory, u'file.pdf'), u'rb') as file_pdf:
                AttachmentAnonymization.objects.create(
                    attachment=attachment_anonymization.attachment,
                    successful=True,
                    file=ContentFile(file_pdf.read()),
                    content_type=content_types.PDF_CONTENT_TYPE,
                    debug=u'STDOUT:\n{}\nSTDERR:\n{}'.format(p.stdout, p.stderr)
                )
            cron_logger.info(u'Anonymized attachment using libreoffice: {}'.format(
                attachment_anonymization))
    except Exception as e:
        trace = unicode(traceback.format_exc(), u'utf-8')
        stdout = p.stdout if p else getattr(e, u'stdout', u'')
        stderr = p.stderr if p else getattr(e, u'stderr', u'')
        AttachmentAnonymization.objects.create(
            attachment=attachment_anonymization.attachment,
            successful=False,
            content_type=content_types.PDF_CONTENT_TYPE,
            debug=u'STDOUT:\n{}\nSTDERR:\n{}\n{}'.format(stdout, stderr, trace)
        )
        cron_logger.error(u'Anonymizing attachment using libreoffice has failed: {}\n An '
                          u'unexpected error occured: {}\n{}'.format(
                                  attachment_anonymization, e.__class__.__name__, trace))

def anonymize_attachment_pdf():
    attachment_anonymizations_pdf = (AttachmentAnonymization.objects
                                     .filter(content_type=content_types.PDF_CONTENT_TYPE))
    attachment_anonymization = (AttachmentAnonymization.objects
            .filter(content_type=content_types.ODT_CONTENT_TYPE,
                    successful=True)
            .exclude(attachment__attachmentanonymization__in=attachment_anonymizations_pdf)
            .first())
    if attachment_anonymization is None:
        return
    else:
        anonymize_pdf(attachment_anonymization)
