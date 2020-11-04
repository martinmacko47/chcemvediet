# vim: expandtab
# -*- coding: utf-8 -*-
import itertools
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase
from django.test.runner import DiscoverRunner

from ..apps.geounits.models import Region, District, Municipality, Neighbourhood
from ..apps.inforequests.models import Branch, Inforequest, InforequestDraft
from ..apps.obligees.models import Obligee, ObligeeTag, ObligeeGroup, ObligeeAlias


class CustomTestRunner(DiscoverRunner):
    u"""
    Custom test runner with the following features:
     -- Disabled logging while testing.
        Source: http://stackoverflow.com/questions/5255657/how-can-i-disable-logging-while-running-unit-tests-in-python-django
     -- Forced language code 'en'
    """

    def setup_test_environment(self, **kwargs):
        super(CustomTestRunner, self).setup_test_environment(**kwargs)
        settings.LANGUAGE_CODE = u'en'

    def run_tests(self, *args, **kwargs):
        logging.disable(logging.CRITICAL)
        return super(CustomTestRunner, self).run_tests(*args, **kwargs)

class ChcemvedietTestCaseMixin(TestCase):

    def _pre_setup(self):
        super(ChcemvedietTestCaseMixin, self)._pre_setup()
        self.counter = itertools.count()
        self.user = self._create_user()
        self.region = self._create_region()
        self.district = self._create_district()
        self.municipality = self._create_municipality()
        self.neighbourhood = self._create_neighbourhood()
        self.inforequest = self._create_inforequest()
        self.obligee = self._create_obligee()
        self.tag = self._create_obligee_tag()
        self.group = self._create_obligee_group()

    def _call_with_defaults(self, func, kwargs, defaults):
        omit = kwargs.pop(u'omit', [])
        defaults.update(kwargs)
        for key in omit:
            del defaults[key]
        return func(**defaults)

    def _create_user(self, **kwargs):
        nr = u'{:03d}'.format(self.counter.next())
        street = kwargs.pop(u'street', u'Default User Street')
        city = kwargs.pop(u'city', u'Default User City')
        zip = kwargs.pop(u'zip', u'00000')
        email_verified = kwargs.pop(u'email_verified', True)
        user = self._call_with_defaults(User.objects.create_user, kwargs, {
                u'username': u'default_testing_username_{}'.format(nr),
                u'first_name': u'Default Testing First Name',
                u'last_name': u'Default Testing Last Name',
                u'email': u'default_testing_mail_{}@a.com'.format(nr),
                u'password': u'default_testing_secret',
                })
        user.profile.street = street
        user.profile.city = city
        user.profile.zip = zip
        user.profile.save()
        if email_verified:
            user.emailaddress_set.create(email=user.email, verified=True)
        return user

    def _create_region(self, **kwargs):
        name = u'SK{:05d}'.format(self.counter.next())
        return self._call_with_defaults(Region.objects.create, kwargs, {
                u'id': name,
                u'name': name,
                })

    def _create_district(self, **kwargs):
        name = u'SK{:05d}'.format(self.counter.next())
        return self._call_with_defaults(District.objects.create, kwargs, {
                u'id': name,
                u'name': name,
                u'region': self.region,
                })

    def _create_municipality(self, **kwargs):
        name = u'SK{:05d}'.format(self.counter.next())
        return self._call_with_defaults(Municipality.objects.create, kwargs, {
                u'id': name,
                u'name': name,
                u'region': self.region,
                u'district': self.district,
                })

    def _create_neighbourhood(self, **kwargs):
        name = u'SK{:05d}'.format(self.counter.next())
        return self._call_with_defaults(Neighbourhood.objects.create, kwargs, {
                u'id': name,
                u'name': name,
                u'region': self.region,
                u'district': self.district,
                u'municipality': self.municipality,
                })

    def _create_obligee(self, **kwargs):
        return self._call_with_defaults(Obligee.objects.create, kwargs, {
                u'official_name': u'Default Testing Official Name',
                u'name': u'Default Testing Name {:03d}'.format(self.counter.next()),
                u'name_genitive': u'Default Testing Name genitive',
                u'name_dative': u'Default Testing Name dative',
                u'name_accusative': u'Default Testing Name accusative',
                u'name_locative': u'Default Testing Name locative',
                u'name_instrumental': u'Default Testing Name instrumental',
                u'gender': Obligee.GENDERS.MASCULINE,
                u'ico': u'00000000',
                u'street': u'Default Testing Street',
                u'city': u'Default Testing City',
                u'zip': u'00000',
                u'iczsj': self.neighbourhood,
                u'emails': u'default_testing_mail@example.com',
                u'latitude': 0.0,
                u'longitude': 0.0,
                u'type': Obligee.TYPES.SECTION_1,
                u'official_description': u'Default testing official description.',
                u'simple_description': u'Default testing simple description.',
                u'status': Obligee.STATUSES.PENDING,
                u'notes': u'Default testing notes.',
                })

    def _create_obligee_tag(self, **kwargs):
        nr = u'{:03d}'.format(self.counter.next())
        return self._call_with_defaults(ObligeeTag.objects.create, kwargs, {
                u'key': u'Default Testing Key {}'.format(nr),
                u'name': u'Default Testing Name {}'.format(nr),
                })

    def _create_obligee_group(self, **kwargs):
        nr = u'{:03d}'.format(self.counter.next())
        return self._call_with_defaults(ObligeeGroup.objects.create, kwargs, {
                u'key': u'Default Testing Key {}'.format(nr),
                u'name': u'Default Testing Name {}'.format(nr),
                u'description': u'Default Testing Description',
                })

    def _create_obligee_alias(self, **kwargs):
        return self._call_with_defaults(ObligeeAlias.objects.create, kwargs, {
                u'obligee': self.obligee,
                u'name': u'Default Testing Name',
                u'description': u'Default testing description.',
                u'notes': u'Default testing notes.',
                })

    def _create_branch(self, **kwargs):
        return self._call_with_defaults(Branch.objects.create, kwargs, {
            u'inforequest': self.inforequest,
            u'obligee': self.obligee,
            })

    def _create_inforequest(self, **kwargs):
        return self._call_with_defaults(Inforequest.objects.create, kwargs, {
                u'applicant': self.user,
                })

    def _create_inforequest_draft(self, **kwargs):
        return self._call_with_defaults(InforequestDraft.objects.create, kwargs, {
                u'applicant': self.user,
                u'subject': [u'Default Testing Subject'],
                u'content': [u'Default Testing Content'],
                })

    def _render(self, template, **context):
        return Template(template).render(Context(context))
