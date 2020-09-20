# vim: expandtab
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase

from chcemvediet.apps.geounits.models import Neighbourhood, Municipality, District, Region
from chcemvediet.apps.inforequests.models import Inforequest, Branch, InforequestDraft

from ..models import Obligee, ObligeeTag, ObligeeGroup, ObligeeAlias


class ObligeesTestCaseMixin(TestCase):

    def _pre_setup(self):
        super(ObligeesTestCaseMixin, self)._pre_setup()
        self.iczsj = self._create_geounit(u'00000')
        self.user = self._create_user()
        self.inforequest = self._create_inforequest()


    def _call_with_defaults(self, func, kwargs, defaults):
        omit = kwargs.pop(u'omit', [])
        defaults.update(kwargs)
        for key in omit:
            del defaults[key]
        return func(**defaults)

    def _create_user(self, **kwargs):
        try:
            tag = u'{}'.format(User.objects.latest(u'pk').pk + 1)
        except User.DoesNotExist:
            tag = u'1'
        street = kwargs.pop(u'street', u'Default User Street')
        city = kwargs.pop(u'city', u'Default User City')
        zip = kwargs.pop(u'zip', u'00000')
        email_verified = kwargs.pop(u'email_verified', True)
        user = self._call_with_defaults(User.objects.create_user, kwargs, {
                u'username': u'default_testing_username_{}'.format(tag),
                u'first_name': u'Default Testing First Name',
                u'last_name': u'Default Testing Last Name',
                u'email': u'default_testing_mail_{}@a.com'.format(tag),
                u'password': u'default_testing_secret',
                })
        user.profile.street = street
        user.profile.city = city
        user.profile.zip = zip
        user.profile.save()
        if email_verified:
            user.emailaddress_set.create(email=user.email, verified=True)
        return user

    def _create_geounit(self, id):
        r = Region.objects.create(id=id, name=u'region_{}'.format(id))
        d = District.objects.create(id=id, name=u'district_{}'.format(id), region=r)
        m = Municipality.objects.create(id=id, name=u'municipality_{}'.format(id), district=d, region=r)
        n = Neighbourhood.objects.create(id=id, name=u'neighbourhood_{}'.format(id), cadastre=u'Cadastre', municipality=m, district=d, region=r)
        return n

    def _create_obligeetag(self, **kwargs):
        return self._call_with_defaults(ObligeeTag.objects.create, kwargs, {
                u'key': u'Default Testing Key',
                u'name': u'Default Testing Name',
                })

    def _create_obligeegroup(self, **kwargs):
        return self._call_with_defaults(ObligeeGroup.objects.create, kwargs, {
                u'key': u'Default Testing Key',
                u'name': u'Default Testing Name',
                u'description': u'Default Testing Description',
                })

    def _create_obligee(self, **kwargs):
        return self._call_with_defaults(Obligee.objects.create, kwargs, {
                u'official_name': u'Default Testing Official Name',
                u'name': u'Default Testing Name',
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
                u'iczsj': self.iczsj,
                u'emails': u'default_testing_mail@example.com',
                u'latitude': 0.0,
                u'longitude': 0.0,
                u'type': Obligee.TYPES.SECTION_1,
                u'official_description': u'Default testing official description.',
                u'simple_description': u'Default testing simple description.',
                u'status': Obligee.STATUSES.PENDING,
                u'notes': u'Default testing notes.',
                })

    def _create_obligeealias(self, **kwargs):
        return self._call_with_defaults(ObligeeAlias.objects.create, kwargs, {
                u'obligee': kwargs.pop(u'obligee'),
                u'name': u'Default Testing Name',
                u'description': u'Default testing description.',
                u'notes': u'Default testing notes.',
                })

    def _create_branch(self, **kwargs):
        return self._call_with_defaults(Branch.objects.create, kwargs, {
            u'inforequest': self.inforequest,
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
