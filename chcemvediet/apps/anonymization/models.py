import logging
import itertools

from django.db import models
from django.utils.functional import cached_property

from poleno import datacheck
from poleno.attachments.models import Attachment
from poleno.attachments.utils import attachment_file_check, attachment_orphaned_file_check
from poleno.utils.models import QuerySet
from poleno.utils.date import utc_now
from poleno.utils.misc import FormatMixin, random_string, squeeze, decorate, adjust_extension


class AttachmentNormalizationQuerySet(QuerySet):
    def order_by_pk(self):
        return self.order_by(u'pk')

class AttachmentNormalization(FormatMixin, models.Model):

    # May NOT be NULL
    attachment = models.ForeignKey(Attachment)

    # May NOT be NULL
    successful = models.BooleanField(default=False,
            help_text=squeeze(u"""
                True if normalization has succeeded, False otherwise.
                """))

    # May be NULL; Random local filename is generated in save() when creating a new object.
    file = models.FileField(upload_to=u'attachment_normalizations', max_length=255, null=True,
            help_text=squeeze(u"""
                NULL if normalization failed or normalization didn't create any file.
                """))

    # May NOT be empty: Extension automatically adjusted in save() when creating new object.
    name = models.CharField(max_length=255,
            help_text=squeeze(u"""
                Attachment file name, e.g. "document.pdf". Extension automatically adjusted when
                creating a new object.
                """))

    # May be NULL
    content_type = models.CharField(max_length=255, null=True,
            help_text=squeeze(u"""
                Attachment content type, e.g. "application/pdf". The value may be specified even if
                normalization failed.
                """))

    # May NOT be NULL; Automatically computed in save() when creating a new object if undefined.
    created = models.DateTimeField(blank=True,
            help_text=squeeze(u"""
                Date and time the attachment was uploaded or received by an email. Leave blank for
                current time.
                """))

    # May be NULL; Automatically computed in save() when creating a new object.
    size = models.IntegerField(null=True, blank=True,
            help_text=squeeze(u"""
                Attachment file size in bytes. NULL if file is NULL. Automatically computed when
                creating a new object.
                """))

    # May NOT be NULL
    debug = models.TextField(blank=True,
            help_text=squeeze(u"""
                Debug message from normalization.
                """))

    # Backward relations added to other models:
    #
    #  -- Attachment.attachment_normalization_set
    #     May be empty

    # Indexes:
    #  -- attachment:       ForeignKey

    objects = AttachmentNormalizationQuerySet.as_manager()

    @cached_property
    def content(self):
        if not self.file:
            return None
        try:
            self.file.open(u'rb')
            return self.file.read()
        except IOError:
            logger = logging.getLogger(u'chcemvediet.apps.anonymization')
            logger.error(u'{} is missing its file: "{}".'.format(self, self.file.name))
            raise
        finally:
            self.file.close()

    @decorate(prevent_bulk_create=True)
    def save(self, *args, **kwargs):
        if self.pk is None:  # Creating a new object
            if self.created is None:
                self.created = utc_now()
            if self.file:
                self.file.name = random_string(10)
                self.size = self.file.size
            self.name = adjust_extension(self.attachment.name, self.content_type)

        super(AttachmentNormalization, self).save(*args, **kwargs)

    def __unicode__(self):
        return format(self.pk)

@datacheck.register
def datachecks(superficial, autofix):
    u"""
    Checks that every ``AttachmentNormalization`` instance, which file is not NULL, has its file
    working, and there are not any orphaned attachment_normalization files.
    """
    # This check is a bit slow. We skip it if running from cron or the user asked for superficial
    # tests only.
    if superficial:
        return
    attachment_normalizations = AttachmentNormalization.objects.all()
    field = AttachmentNormalization._meta.get_field(u'file')
    return itertools.chain(attachment_file_check(attachment_normalizations),
                           attachment_orphaned_file_check(attachment_normalizations, field,
                                                          AttachmentNormalization.__name__))
