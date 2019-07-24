from django.core.files.base import ContentFile

from poleno.cron import cron_job, cron_logger
from poleno.attachments.models import Attachment
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
    else:
        AttachmentNormalization.objects.create(
            attachment=attachment,
            successful=False,
            content_type=None,
            debug=u'Not supported content type'
        )
        cron_logger.info(u'Skipping normalization of attachment with not supported content '
                         u'type: {}'.format(attachment))
