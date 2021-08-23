# vim: expandtab
# -*- coding: utf-8 -*-
from django.test import TestCase

from poleno.utils.test import ViewTestCaseMixin
from poleno.utils.urls import reverse

from .. import InforequestsTestCaseMixin
from ...models import Action


class MineViewTest(InforequestsTestCaseMixin, ViewTestCaseMixin, TestCase):
    u"""
    Tests ``mine()`` view registered as "inforequests:mine".
    """

    def _create_successful_inforequest(self, applicant):
        inforequest, _, _ = self._create_inforequest_scenario(applicant, {u'closed': True},
                (u'disclosure', dict(disclosure_level=Action.DISCLOSURE_LEVELS.PARTIAL)))
        return inforequest


    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'inforequests:mine'))

    def test_anonymous_user_is_redirected(self):
        self.assert_anonymous_user_is_redirected(reverse(u'inforequests:mine'))

    def test_authenticated_user_gets_inforequest_mine(self):
        self._login_user(self.user1)
        response = self.client.get(reverse(u'inforequests:mine'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'inforequests/mine/mine.html')

    def test_user_gets_only_his_inforequests_and_drafts(self):
        drafts1 = [self._create_inforequest_draft(applicant=self.user1) for i in range(5)]
        drafts2 = [self._create_inforequest_draft(applicant=self.user2) for i in range(3)]
        pending_inforequests1 = [self._create_inforequest(applicant=self.user1) for i in range(4)]
        pending_inforequests2 = [self._create_inforequest(applicant=self.user2) for i in range(5)]
        successful_inforequests1 = [self._create_successful_inforequest(applicant=self.user1) for i in range(3)]
        successful_inforequests2 = [self._create_successful_inforequest(applicant=self.user2) for i in range(3)]
        unsuccessful_inforequests1 = [self._create_inforequest(applicant=self.user1, closed=True) for i in range(3)]
        unsuccessful_inforequests2 = [self._create_inforequest(applicant=self.user2, closed=True) for i in range(3)]

        self._login_user(self.user1)
        response = self.client.get(reverse(u'inforequests:mine'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.context[u'pending_inforequests'], pending_inforequests1)
        self.assertItemsEqual(response.context[u'drafts'], drafts1)
        self.assertItemsEqual(response.context[u'successful_inforequests'], successful_inforequests1)
        self.assertItemsEqual(response.context[u'unsuccessful_inforequests'], unsuccessful_inforequests1)

    def test_with_user_with_no_his_inforequests_nor_drafts(self):
        drafts2 = [self._create_inforequest_draft(applicant=self.user2) for i in range(3)]
        pending_inforequests2 = [self._create_inforequest(applicant=self.user2) for i in range(5)]
        successful_inforequests2 = [self._create_successful_inforequest(applicant=self.user2) for i in range(3)]
        unsuccessful_inforequests2 = [self._create_inforequest(applicant=self.user2, closed=True) for i in range(3)]

        self._login_user(self.user1)
        response = self.client.get(reverse(u'inforequests:mine'))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.context[u'pending_inforequests'], [])
        self.assertItemsEqual(response.context[u'drafts'], [])
        self.assertItemsEqual(response.context[u'successful_inforequests'], [])
        self.assertItemsEqual(response.context[u'unsuccessful_inforequests'], [])

    def test_related_models_are_prefetched_before_render(self):
        drafts1 = [self._create_inforequest_draft(applicant=self.user1) for i in range(5)]
        pending_inforequests1 = [self._create_inforequest(applicant=self.user1) for i in range(4)]
        successful_inforequests1 = [self._create_successful_inforequest(applicant=self.user1) for i in range(3)]
        unsuccessful_inforequests1 = [self._create_inforequest(applicant=self.user1, closed=True) for i in range(3)]

        # Force view querysets to evaluate before calling render
        def pre_mock_render(request, template, context):
            list(context[u'pending_inforequests'])
            list(context[u'drafts'])
            list(context[u'successful_inforequests'])
            list(context[u'unsuccessful_inforequests'])

        self._login_user(self.user1)
        with self.assertQueriesDuringRender([], pre_mock_render=pre_mock_render):
            response = self.client.get(reverse(u'inforequests:mine'))
        self.assertEqual(response.status_code, 200)
