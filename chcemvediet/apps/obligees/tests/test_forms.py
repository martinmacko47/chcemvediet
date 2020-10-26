# vim: expandtab
# -*- coding: utf-8 -*-
import lxml.html
from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from poleno.utils.urls import reverse

from chcemvediet.tests import ChcemvedietTestCaseMixin

from ..forms import ObligeeWidget, ObligeeField


class ObligeeFieldTest(ChcemvedietTestCaseMixin, TestCase):
    u"""
    Tests ``ObligeeField`` field with ``ObligeeWidget`` widget.
    """

    class Form(forms.Form):
        obligee = ObligeeField()

    class FormWithWidgetAttrs(forms.Form):
        obligee = ObligeeField(
                widget=ObligeeWidget(input_attrs={
                    u'class': u'custom-class',
                    u'custom-attribute': u'value',
                    }),
                )


    def test_new_form(self):
        form = self.Form()
        rendered = self._render(u'{{ form }}', form=form)
        html = lxml.html.fromstring(rendered)

        self.assertInHTML(u'<label for="id_obligee">Obligee:</label>', rendered)
        root = html.get_element_by_id(u'id_obligee')
        self.assertEqual(root.tag, u'div')
        self.assertEqual(root.attrib[u'class'], u'chv-obligee-widget')

        inputs = root.find_class(u'chv-obligee-widget-inputs')[0]
        self.assertEqual(inputs.tag, u'div')
        input = inputs.find_class(u'chv-obligee-widget-input')[0]
        self.assertEqual(input.tag, u'div')
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)

        details = input.find_class(u'chv-obligee-widget-details chv-obligee-widget-hide')[0]
        self.assertEqual(details.tag, u'div')
        street = details.find_class(u'chv-obligee-widget-street')[0]
        self.assertEqual(street.tag, u'span')
        self.assertIsNone(street.text)
        zip = details.find_class(u'chv-obligee-widget-zip')[0]
        self.assertEqual(zip.tag, u'span')
        self.assertIsNone(zip.text)
        city = details.find_class(u'chv-obligee-widget-city')[0]
        self.assertEqual(city.tag, u'span')
        self.assertIsNone(city.text)
        email = details.find_class(u'chv-obligee-widget-email')[0]
        self.assertEqual(email.tag, u'span')
        self.assertIsNone(email.text)

    def test_new_form_with_custom_widget_class_and_attributes(self):
        form = self.FormWithWidgetAttrs()
        rendered = self._render(u'{{ form }}', form=form)
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete custom-class" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="" custom-attribute="value">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)

    def test_new_form_with_initial_value_as_obligee_instance(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n, street=u'{} street'.format(n), city=u'{} city'.format(n), zip=u'12345', emails=u'{}@a.com'.format(n)) for n in names]
        form = self.Form(initial={u'obligee': oblgs[2]})
        rendered = self._render(u'{{ form }}', form=form)
        html = lxml.html.fromstring(rendered)
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="ccc">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)
        details = html.find_class(u'chv-obligee-widget-details')[0]
        street = details.find_class(u'chv-obligee-widget-street')[0]
        self.assertEqual(street.text, u'ccc street')
        zip = details.find_class(u'chv-obligee-widget-zip')[0]
        self.assertEqual(zip.text, u'12345')
        city = details.find_class(u'chv-obligee-widget-city')[0]
        self.assertEqual(city.text, u'ccc city')
        email = details.find_class(u'chv-obligee-widget-email')[0]
        self.assertEqual(email.text, u'ccc@a.com')

    def test_new_form_with_initial_value_as_obligee_name(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n, street=u'{} street'.format(n), city=u'{} city'.format(n), zip=u'12345', emails=u'{}@a.com'.format(n)) for n in names]
        form = self.Form(initial={u'obligee': u'ccc'})
        rendered = self._render(u'{{ form }}', form=form)
        html = lxml.html.fromstring(rendered)
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="ccc">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)
        details = html.find_class(u'chv-obligee-widget-details')[0]
        street = details.find_class(u'chv-obligee-widget-street')[0]
        self.assertEqual(street.text, u'ccc street')
        zip = details.find_class(u'chv-obligee-widget-zip')[0]
        self.assertEqual(zip.text, u'12345')
        city = details.find_class(u'chv-obligee-widget-city')[0]
        self.assertEqual(city.text, u'ccc city')
        email = details.find_class(u'chv-obligee-widget-email')[0]
        self.assertEqual(email.text, u'ccc@a.com')

    def test_submitted_with_empty_value_but_required(self):
        form = self.Form({u'obligee': u''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[u'obligee'], [u'This field is required.'])

        rendered = self._render(u'{{ form }}', form=form)
        self.assertInHTML(u'<ul class="errorlist"><li>This field is required.</li></ul>', rendered)

    def test_submitted_with_empty_value_but_not_required(self):
        form = self.Form({u'obligee': u''})
        form.fields[u'obligee'].required = False
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data[u'obligee'])

        rendered = self._render(u'{{ form }}', form=form)
        self.assertInHTML(u'<ul class="errorlist"><li>This field is required.</li></ul>', rendered, count=0)

    def test_submitted_with_valid_obligee_name(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n, street=u'{} street'.format(n), city=u'{} city'.format(n), zip=u'12345', emails=u'{}@a.com'.format(n)) for n in names]
        form = self.Form({u'obligee': u'bbb'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data[u'obligee'], oblgs[1])

        rendered = self._render(u'{{ form }}', form=form)
        html = lxml.html.fromstring(rendered)
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="bbb">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)
        details = html.find_class(u'chv-obligee-widget-details')[0]
        street = details.find_class(u'chv-obligee-widget-street')[0]
        self.assertEqual(street.text, u'bbb street')
        zip = details.find_class(u'chv-obligee-widget-zip')[0]
        self.assertEqual(zip.text, u'12345')
        city = details.find_class(u'chv-obligee-widget-city')[0]
        self.assertEqual(city.text, u'bbb city')
        email = details.find_class(u'chv-obligee-widget-email')[0]
        self.assertEqual(email.text, u'bbb@a.com')

    def test_submitted_with_nonexisting_obligee_name(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n) for n in names]
        form = self.Form({u'obligee': u'invalid'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[u'obligee'], [_(u'obligees:ObligeeField:error:invalid_obligee')])

        rendered = self._render(u'{{ form }}', form=form)
        html = lxml.html.fromstring(rendered)
        self.assertInHTML(u'<ul class="errorlist"><li>{}</li></ul>'.format(_(u'obligees:ObligeeField:error:invalid_obligee')), rendered)
        self.assertInHTML(u"""
                <input class="form-control pln-autocomplete" data-autocomplete-url="{url}" name="obligee" data-name="obligee" type="text" value="invalid">
                """.format(url=reverse(u'obligees:autocomplete')), rendered)
        details = html.find_class(u'chv-obligee-widget-details')[0]
        street = details.find_class(u'chv-obligee-widget-street')[0]
        self.assertIsNone(street.text)
        zip = details.find_class(u'chv-obligee-widget-zip')[0]
        self.assertIsNone(zip.text)
        city = details.find_class(u'chv-obligee-widget-city')[0]
        self.assertIsNone(city.text)
        email = details.find_class(u'chv-obligee-widget-email')[0]
        self.assertIsNone(email.text)

    def test_to_python_is_cached(self):
        names = [u'aaa', u'bbb', u'ccc', u'ddd']
        oblgs = [self._create_obligee(name=n) for n in names]
        field = ObligeeField()

        # Valid value
        with self.assertNumQueries(1):
            self.assertEqual(field.clean(u'bbb'), oblgs[1])
        with self.assertNumQueries(0):
            self.assertEqual(field.clean(u'bbb'), oblgs[1])

        # Invalid value
        with self.assertNumQueries(1):
            with self.assertRaises(ValidationError):
                field.clean(u'invalid')
        with self.assertNumQueries(0):
            with self.assertRaises(ValidationError):
                field.clean(u'invalid')
