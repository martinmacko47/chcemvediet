# vim: expandtab
# -*- coding: utf-8 -*-
from django.template import Context, Template

from chcemvediet.tests import ChcemvedietTestCaseMixin

from ..models import ObligeeTag, ObligeeGroup, ObligeeAlias


class ObligeesTestCaseMixin(ChcemvedietTestCaseMixin):

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

    def _create_obligeealias(self, **kwargs):
        return self._call_with_defaults(ObligeeAlias.objects.create, kwargs, {
                u'obligee': self.obligee,
                u'name': u'Default Testing Name',
                u'description': u'Default testing description.',
                u'notes': u'Default testing notes.',
                })

    def _render(self, template, **context):
        return Template(template).render(Context(context))
