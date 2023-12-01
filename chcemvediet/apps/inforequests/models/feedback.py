# vim: expandtab
# -*- coding: utf-8 -*-
from django.db import models

from poleno.utils.date import utc_now
from poleno.utils.misc import FormatMixin
from poleno.utils.models import QuerySet


class FeedbackQuerySet(QuerySet):
    def order_by_pk(self):
        return self.order_by(u'pk')


class Feedback(FormatMixin, models.Model):
    # NOT NULL
    inforequest = models.ForeignKey(u'Inforequest', db_index=False)

    # May be empty
    content = models.TextField(blank=True)

    # NOT NULL
    created = models.DateTimeField(default=utc_now)

    # Indexes:
    #  -- inforequest: ForeignKey
    #  -- created, id: index_together

    objects = FeedbackQuerySet.as_manager()

    class Meta:
        verbose_name_plural = u'Feedback'
        index_together = [
            [u'created', u'id'],
        ]
