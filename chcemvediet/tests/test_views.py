# vim: expandtab
# -*- coding: utf-8 -*-
import unittest

from django.core.urlresolvers import reverse
from django.test import TestCase

from poleno.utils.test import ViewTestCaseMixin

class IndexViewTest(ViewTestCaseMixin, TestCase):
    u"""
    Tests ``index()`` view registered as "index".
    """

    @unittest.skip(u'FIXME')
    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'index'))

    @unittest.skip(u'FIXME')
    def test_index(self):
        response = self.client.get(reverse(u'index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'main/pages/index.en.html')

class AboutViewTest(ViewTestCaseMixin, TestCase):
    u"""
    Tests ``about()`` view registered as "about".
    """

    @unittest.skip(u'FIXME')
    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'about'))

    @unittest.skip(u'FIXME')
    def test_about(self):
        response = self.client.get(reverse(u'about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'main/pages/about.en.html')
