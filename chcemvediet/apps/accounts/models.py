# vim: expandtab
# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.contrib.auth.models import User
from aggregate_if import Count
from jsonfield import JSONField

from poleno.mail.models import Message
from poleno.utils.models import QuerySet
from poleno.utils.misc import FormatMixin, squeeze
from chcemvediet.apps.inforequests.models import InforequestEmail


class ProfileQuerySet(QuerySet):
    def select_undecided_emails_count(self):
        u"""
        Use to select ``Profile.undecided_emails_count``.
        """
        return self.annotate(undecided_emails_count=Count(u'user__inforequest__inforequestemail',
                only=Q(user__inforequest__inforequestemail__type=InforequestEmail.TYPES.UNDECIDED)))

class Profile(FormatMixin, models.Model):
    user = models.OneToOneField(User)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=10)

    anonymize_inforequests = models.BooleanField(default=True,
            help_text=squeeze(u"""
                If true, published inforequests will be shown anonymized, otherwise in their
                original version.
                """))
    custom_anonymized_strings = JSONField(null=True, default=None,
            help_text=squeeze(u"""
                User defined strings for anonymization. NULL for default anonymization.
                """))


    # Backward relations added to other models:
    #
    #  -- User.profile
    #     Should NOT raise DoesNotExist

    # Indexes:
    #  -- user: OneToOneField

    objects = ProfileQuerySet.as_manager()

    @property
    def undecided_emails_set(self):
        u"""
        Queryset of all undecided emails assigned to inforequests owned by the user.
        """
        return Message.objects.filter(
                inforequest__closed=False,
                inforequest__applicant_id=self.user_id,
                inforequestemail__type=InforequestEmail.TYPES.UNDECIDED,
                )

    @cached_property
    def undecided_emails(self):
        u"""
        Cached list of all undecided emails assigned to inforequests owned by the user. The emails
        are ordered by ``processed``.
        """
        return list(self.undecided_emails_set.order_by_processed())

    @cached_property
    def undecided_emails_count(self):
        u"""
        Cached number of undecided emails assigned to inforequests owned by the user. May be
        prefetched with ``select_undecided_emails_count()`` queryset method, Takes advantage of
        ``Profile.undecided_emails`` if it is already fetched.
        """
        if u'undecided_emails' in self.__dict__:
            return len(self.undecided_emails)
        else:
            return self.undecided_emails_set.count()

    @cached_property
    def has_undecided_emails(self):
        u"""
        Cached flag if the user has any undecided emails assigned to his inforequests. Takes
        advantage of ``Profile.undecided_emails_count`` or ``Profile.undecided_emails`` if either
        is already fetched.
        """
        if u'undecided_emails_count' in self.__dict__:
            return bool(self.undecided_emails_count)
        elif u'undecided_emails' in self.__dict__:
            return bool(self.undecided_emails)
        else:
            return self.undecided_emails_set.exists()

    def __unicode__(self):
        return format(self.pk)
