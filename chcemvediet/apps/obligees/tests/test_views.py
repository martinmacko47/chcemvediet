# vim: expandtab
# -*- coding: utf-8 -*-
import random
import json

from django.http import JsonResponse
from django.test import TestCase

from poleno.utils.test import ViewTestCaseMixin
from poleno.utils.urls import reverse

from . import ObligeesTestCaseMixin
from ..constants import OBLIGEES_PER_PAGE
from ..models import Obligee


class IndexViewTest(ObligeesTestCaseMixin, ViewTestCaseMixin, TestCase):
    u"""
    Tests ``index()`` view registered as "obligees:index".
    """

    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'obligees:index'))

    def test_obligees_index(self):
        response = self.client.get(reverse(u'obligees:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'obligees/index.html')

    def test_paginator_with_no_page_number_shows_first_page(self):
        oblgs = [self._create_obligee(name=u'Agency_{:03d}'.format(i+1)) for i in range(2*OBLIGEES_PER_PAGE+1)]
        response = self.client.get(reverse(u'obligees:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[u'obligee_page']), u'<Page 1 of 3>')
        self.assertEqual(list(response.context[u'obligee_page']), oblgs[:OBLIGEES_PER_PAGE])

    def test_paginator_with_valid_page_number_shows_requested_page(self):
        oblgs = [self._create_obligee(name=u'Agency_{:03d}'.format(i+1)) for i in range(2*OBLIGEES_PER_PAGE+1)]
        response = self.client.get(reverse(u'obligees:index') + u'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[u'obligee_page']), u'<Page 2 of 3>')
        self.assertEqual(list(response.context[u'obligee_page']), oblgs[25:50])

    def test_paginator_with_too_high_page_number_shows_last_page(self):
        oblgs = [self._create_obligee(name=u'Agency_{:03d}'.format(i+1)) for i in range(2*OBLIGEES_PER_PAGE+1)]
        response = self.client.get(reverse(u'obligees:index') + u'?page=47')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[u'obligee_page']), u'<Page 3 of 3>')
        self.assertEqual(list(response.context[u'obligee_page']), oblgs[50:])

    def test_paginator_with_invalid_page_number_shows_first_page(self):
        oblgs = [self._create_obligee(name=u'Agency_{:03d}'.format(i+1)) for i in range(2*OBLIGEES_PER_PAGE+1)]
        response = self.client.get(reverse(u'obligees:index') + u'?page=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[u'obligee_page']), u'<Page 1 of 3>')
        self.assertEqual(list(response.context[u'obligee_page']), oblgs[:25])

    def test_paginator_with_no_obligees(self):
        response = self.client.get(reverse(u'obligees:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[u'obligee_page']), u'<Page 1 of 1>')
        self.assertEqual(list(response.context[u'obligee_page']), [])

class AutocompleteViewTest(ObligeesTestCaseMixin, ViewTestCaseMixin, TestCase):
    u"""
    Tests ``autocomplete()`` view registered as "obligees:autocomplete".
    """

    def test_allowed_http_methods(self):
        allowed = [u'HEAD', u'GET']
        self.assert_allowed_http_methods(allowed, reverse(u'obligees:autocomplete'))

    def test_autocomplete_returns_json_with_correct_structure(self):
        neighbourhood1 = self._create_geounit(u'11122')
        oblg1 = self._create_obligee(
                official_name=u'Agency Official',
                name=u'Agency',
                name_genitive=u'Agency (G)',
                name_dative=u'Agency (D)',
                name_accusative=u'Agency (A)',
                name_locative=u'Agency (L)',
                name_instrumental=u'Agency (I)',
                gender=Obligee.GENDERS.MASCULINE,
                ico=u'12345678',
                street=u'Westend',
                city=u'Winterfield',
                zip=u'12345',
                iczsj=neighbourhood1,
                emails=u'agency@a.com',
                latitude=13.48,
                longitude=-78.159,
                type=Obligee.TYPES.SECTION_1,
                official_description=u'Agency\'s official description.',
                simple_description=u'Agency\'s simple description.',
                status=Obligee.STATUSES.PENDING,
                notes=u'Notes about agency.',
                )
        obligeetag1 = self._create_obligeetag(key=u'ObligeeTag 1', name=u'ObligeeTag 1 name')
        obligeetag2 = self._create_obligeetag(key=u'ObligeeTag 2', name=u'ObligeeTag 2 name')
        obligeegroup = self._create_obligeegroup(key=u'ObligeeGroup 1', name=u'ObligeeGroup 1 name')
        oblg1.tags.add(obligeetag1, obligeetag2)
        oblg1.groups.add(obligeegroup)
        neighbourhood2 = self._create_geounit(u'11133')
        oblg2 = self._create_obligee(
            official_name=u'Ministry Official',
            name=u'Ministry',
            name_genitive=u'Ministry (G)',
            name_dative=u'Ministry (D)',
            name_accusative=u'Ministry (A)',
            name_locative=u'Ministry (L)',
            name_instrumental=u'Ministry (I)',
            gender=Obligee.GENDERS.FEMININE,
            ico=u'12341234',
            street=u'Eastend',
            city=u'Springfield',
            zip=u'12345',
            iczsj=neighbourhood2,
            emails=u'ministry@a.com',
            latitude=22.12,
            longitude=3.672,
            type=Obligee.TYPES.SECTION_2,
            official_description=u'Ministry\'s official description.',
            simple_description=u'Ministry\'s simple description.',
            slug=u'ministry',
            status=Obligee.STATUSES.PENDING,
            notes=u'Notes about ministry.',
        )
        response = self.client.get(reverse(u'obligees:autocomplete'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        data = json.loads(response.content)
        self.assertEqual(data, [
                {
                u'label': u'Agency',
                u'obligee': {
                    u'id': oblg1.pk,
                    u'official_name': u'Agency Official',
                    u'name': u'Agency',
                    u'name_genitive': u'Agency (G)',
                    u'name_dative': u'Agency (D)',
                    u'name_accusative': u'Agency (A)',
                    u'name_locative': u'Agency (L)',
                    u'name_instrumental': u'Agency (I)',
                    u'gender': Obligee.GENDERS.MASCULINE,
                    u'ico': u'12345678',
                    u'street': u'Westend',
                    u'city': u'Winterfield',
                    u'zip': u'12345',
                    u'iczsj': neighbourhood1.id,
                    u'emails': u'agency@a.com',
                    u'latitude': 13.48,
                    u'longitude': -78.159,
                    u'tags': [obligeetag1.pk, obligeetag2.pk],
                    u'groups': [obligeegroup.pk],
                    u'type': Obligee.TYPES.SECTION_1,
                    u'official_description': u'Agency\'s official description.',
                    u'simple_description': u'Agency\'s simple description.',
                    u'slug': u'agency',
                    u'status': Obligee.STATUSES.PENDING,
                    u'notes': u'Notes about agency.',
                    },
                },
                {
                u'label': u'Ministry',
                u'obligee': {
                    u'id': oblg2.pk,
                    u'official_name': u'Ministry Official',
                    u'name': u'Ministry',
                    u'name_genitive': u'Ministry (G)',
                    u'name_dative': u'Ministry (D)',
                    u'name_accusative': u'Ministry (A)',
                    u'name_locative': u'Ministry (L)',
                    u'name_instrumental': u'Ministry (I)',
                    u'gender': Obligee.GENDERS.FEMININE,
                    u'ico': u'12341234',
                    u'street': u'Eastend',
                    u'city': u'Springfield',
                    u'zip': u'12345',
                    u'iczsj': neighbourhood2.id,
                    u'emails': u'ministry@a.com',
                    u'latitude': 22.12,
                    u'longitude': 3.672,
                    u'tags': [],
                    u'groups': [],
                    u'type': Obligee.TYPES.SECTION_2,
                    u'official_description': u'Ministry\'s official description.',
                    u'simple_description': u'Ministry\'s simple description.',
                    u'slug': u'ministry',
                    u'status': Obligee.STATUSES.PENDING,
                    u'notes': u'Notes about ministry.',
                    },
                },
            ])

    def test_autocomplete_is_case_insensitive(self):
        names = [u'aaa 1', u'AAA 2', u'AaA 3', u'ddd 1', u'Ddd 2', u'eee']
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aAa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aaa 1', u'AAA 2', u'AaA 3'])

    def test_autocomplete_ignores_accents(self):
        names = [u'aáá 1', u'aää 2', u'aÁÄ 3', u'aaa 4', u'ddd', u'eee']
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=ǎaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aáá 1', u'aää 2', u'aÁÄ 3', u'aaa 4'])

    def test_autocomplete_with_multiple_words(self):
        names = [u'aaa bbb ccc', u'bbb aaa', u'aaa ccc', u'ddd']
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=++aaa++bbb,ccc++,,++')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aaa bbb ccc'])

    def test_autocomplete_matches_obligee_name_prefixes(self):
        names = [u'aa', u'aaa', u'aaaaaaa', u'aaaxxxx', u'xxxxaaa', u'xxxxaaaxxxx', u'xxx aaa', u'xxx aaax xxx']
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aaa', u'aaaaaaa', u'aaaxxxx', u'xxxxaaa', u'xxxxaaaxxxx', u'xxx aaa', u'xxx aaax xxx'])

    def test_autocomplete_without_term_returns_everything(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aaa', u'bbb', u'ccc', u'ddd'])

    def test_autocomplete_returns_only_pending_obligees(self):
        oblg1 = self._create_obligee(name=u'aaa 1', status=Obligee.STATUSES.PENDING)
        oblg2 = self._create_obligee(name=u'aaa 2', status=Obligee.STATUSES.PENDING)
        oblg3 = self._create_obligee(name=u'aaa 3', status=Obligee.STATUSES.DISSOLVED)
        oblg4 = self._create_obligee(name=u'aaa 4', status=Obligee.STATUSES.DISSOLVED)
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertItemsEqual(found, [u'aaa 1', u'aaa 2'])

    def test_autocomplete_returns_at_most_50_obligees(self):
        oblgs = [self._create_obligee(name=u'aaa_{:03d}'.format(i)) for i in range(75)]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 50)

    def test_autocomplete_returns_obligees_ordered_by_name(self):
        names = [u'aaa', u'aaa bbb1', u'aaa bbb2', u'aaa ccc', u'aaa ddd', u'eee aaa', u'fff', u'ggg aaa', u'hhh']
        random.shuffle(names)
        oblgs = [self._create_obligee(name=n) for n in names]
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = [d[u'obligee'][u'name'] for d in data]
        self.assertEqual(found, [u'aaa', u'aaa bbb1', u'aaa bbb2', u'aaa ccc', u'aaa ddd', u'eee aaa', u'ggg aaa'])

    def test_autocomplete_with_no_obligees(self):
        response = self.client.get(reverse(u'obligees:autocomplete') + u'?term=aaa')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])
