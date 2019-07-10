# vim: expandtab
# -*- coding: utf-8 -*-
import datetime
import logging

import magic
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from poleno import datacheck
from poleno.utils.models import QuerySet
from poleno.utils.date import utc_now, utc_datetime_from_local
from poleno.utils.misc import FormatMixin, random_string, squeeze, decorate


class AttachmentQuerySet(QuerySet):
    def attached_to(self, *args):
        u"""
        Filter attachments attached to any of given arguments. As an argument you may pass:
         -- model instance: filters attachments attached to the instance;
         -- model class: filters attachments attached to any instance of the model;
         -- queryset: filters attachments attached to any of the objects returned by the queryset.
        """
        q = []
        for arg in args:
            if isinstance(arg, models.query.QuerySet):
                content_type = ContentType.objects.get_for_model(arg.model)
                q.append(Q(generic_type=content_type, generic_id__in=arg.values(u'pk')))
            elif isinstance(arg, models.Model):
                content_type = ContentType.objects.get_for_model(arg.__class__)
                q.append(Q(generic_type=content_type, generic_id=arg.pk))
            elif isinstance(arg, type) and issubclass(arg, models.Model):
                content_type = ContentType.objects.get_for_model(arg)
                q.append(Q(generic_type=content_type))
            else:
                raise TypeError(u'Expecting QuerySet, Model instance, or Model class.')
        q = reduce((lambda a, b: a | b), q, Q())
        return self.filter(q)
    def order_by_pk(self):
        return self.order_by(u'pk')

class Attachment(FormatMixin, models.Model):
    # May NOT be NULL; Generic relation; Index is prefix of [generic_type, generic_id] index
    generic_type = models.ForeignKey(ContentType, db_index=False)
    generic_id = models.CharField(max_length=255)
    generic_object = generic.GenericForeignKey(u'generic_type', u'generic_id')

    # May NOT be NULL; Random local filename is generated in save() when creating a new object.
    file = models.FileField(upload_to=u'attachments', max_length=255)

    # May be empty; May NOT be trusted, set by client.
    name = models.CharField(max_length=255,
            help_text=squeeze(u"""
                Attachment file name, e.g. "document.pdf". The value does not have to be a valid
                filename. It may be set by the user.
                """))

    # May NOT be empty: Automatically computed in save() when creating a new object.
    content_type = models.CharField(max_length=255,
            help_text=squeeze(u"""
                Attachment content type, e.g. "application/pdf". Automatically computed when
                creating a new object.
                """))

    # May NOT be NULL; Automaticly computed in save() when creating a new object if undefined.
    created = models.DateTimeField(blank=True,
            help_text=squeeze(u"""
                Date and time the attachment was uploaded or received by an email. Leave blank for
                current time.
                """))

    # May NOT by NULL; Automatically computed in save() when creating a new object.
    size = models.IntegerField(blank=True,
            help_text=squeeze(u"""
                Attachment file size in bytes. Automatically computed when creating a new object.
                """))

    # Indexes:
    #  -- generic_type, generic_id: index_together

    objects = AttachmentQuerySet.as_manager()

    class Meta:
        index_together = [
                [u'generic_type', u'generic_id'],
                ]

    @cached_property
    def content(self):
        try:
            self.file.open(u'rb')
            return self.file.read()
        except IOError:
            logger = logging.getLogger(u'poleno.attachments')
            logger.error(u'{} is missing its file: "{}".'.format(self, self.file.name))
            raise
        finally:
            self.file.close()

    @decorate(prevent_bulk_create=True)
    def save(self, *args, **kwargs):
        if self.pk is None: # Creating a new object
            self.file.name = random_string(10)
            if self.created is None:
                self.created = utc_now()
            self.size = self.file.size
            self.content_type = magic.from_buffer(self.file.read(), mime=True)

        super(Attachment, self).save(*args, **kwargs)

    def clone(self, generic_object):
        u""" The returned copy is not saved. """
        return Attachment(
                generic_object=generic_object,
                file=ContentFile(self.content),
                name=self.name,
                created=self.created,
                )

    def __unicode__(self):
        return format(self.pk)

@datacheck.register
def datachecks(superficial, autofix):
    u"""
    Checks that every ``Attachment`` instance has its file working, and there are not any orphaned
    attachment files.
    """
    # This check is a bit slow. We skip it if running from cron or the user asked for
    # superficial tests only.
    if superficial:
        return

    attachments = Attachment.objects.all()
    attachment_names = {a.file.name for a in attachments}

    for attachment in attachments:
        try:
            try:
                attachment.file.open(u'rb')
            finally:
                attachment.file.close()
        except IOError:
            yield datacheck.Error(u'{} is missing its file: "{}".',
                    attachment, attachment.file.name)

    field = Attachment._meta.get_field(u'file')
    if not field.storage.exists(field.upload_to):
        return
    for file_name in field.storage.listdir(field.upload_to)[1]:
        attachment_name = u'{}/{}'.format(field.upload_to, file_name)
        modified_time = utc_datetime_from_local(field.storage.modified_time(attachment_name))
        timedelta = utc_now() - modified_time
        if timedelta > datetime.timedelta(days=5) and attachment_name not in attachment_names:
            yield datacheck.Info(squeeze(u"""
                    There is no Attachment instance for file: "{}". The file is {} days old, so you
                    can probably remove it.
                    """), attachment_name, timedelta.days)
