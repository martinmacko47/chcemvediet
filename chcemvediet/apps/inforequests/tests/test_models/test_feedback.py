# vim: expandtab
# -*- coding: utf-8 -*-

import datetime
import random

from django.db import IntegrityError
from django.test import TestCase

from poleno.utils.date import local_datetime_from_local, utc_now

from .. import InforequestsTestCaseMixin
from ...models import Feedback


class FeedbackTest(InforequestsTestCaseMixin, TestCase):
    def test_inforequest_field(self):
        inforequest = self._create_inforequest(applicant=self.user1)
        feedback = self._create_feedback(inforequest=inforequest)
        self.assertEqual(feedback.inforequest, inforequest)

    def test_inforequest_field_may_not_be_null(self):
        with self.assertRaisesMessage(IntegrityError, u'NOT NULL constraint failed: inforequests_feedback.inforequest_id'):
            self._create_feedback(omit=[u'inforequest'])

    def test_content_field(self):
        feedback = self._create_feedback(content=u'Content')
        self.assertEqual(feedback.content, u'Content')

    def test_created_field(self):
        dt = local_datetime_from_local(u'2023-12-01 09:20:00.223445')
        feedback = self._create_feedback(created=dt)
        self.assertEqual(feedback.created, dt)

    def test_created_field_default_value_if_omitted(self):
        feedback = self._create_feedback(omit=[u'created'])
        self.assertAlmostEqual(feedback.created, utc_now(), delta=datetime.timedelta(milliseconds=100))

    def test_order_by_pk_query_method(self):
        feedback = [self._create_feedback() for _ in range(20)]
        sample = random.sample(feedback, 10)
        result = Feedback.objects.filter(pk__in=(d.pk for d in sample)).order_by_pk().reverse()
        self.assertEqual(list(result), sorted(sample, key=lambda d: -d.pk))

