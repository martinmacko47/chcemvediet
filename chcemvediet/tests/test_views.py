# vim: expandtab
# -*- coding: utf-8 -*-
from django.test import TestCase

from poleno.utils.test import ViewTestCaseMixin
from poleno.utils.urls import reverse


class HomepageViewTest(ViewTestCaseMixin, TestCase):
    u"""
    Tests ``homepage()`` view registered as "homepage".
    """

    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'homepage'))

    def test_homepage(self):
        response = self.client.get(reverse(u'homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'main/homepage/main.html')

class SearchViewTest(ViewTestCaseMixin, TestCase):
    u"""
    Tests ``search()`` view registered as "search".
    """

    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'search'))

    def test_search(self):
        response = self.client.get(reverse(u'search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'main/search/search.html')
