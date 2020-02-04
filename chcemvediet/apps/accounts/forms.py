# vim: expandtab
# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from chcemvediet.apps.anonymization.anonymization import WORD_SIZE_MIN
from chcemvediet.apps.anonymization.models import AttachmentAnonymization, AttachmentFinalization


class SignupForm(forms.Form):
    first_name = forms.CharField(
            max_length=30,
            label=_(u'accounts:SignupForm:first_name:label'),
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'accounts:SignupForm:first_name:placeholder'),
                }),
            )
    last_name = forms.CharField(
            max_length=30,
            label=_(u'accounts:SignupForm:last_name:label'),
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'accounts:SignupForm:last_name:placeholder'),
                }),
            )
    street = forms.CharField(
            max_length=100,
            label=_(u'accounts:SignupForm:street:label'),
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'accounts:SignupForm:street:placeholder'),
                }),
            )
    city = forms.CharField(
            max_length=30,
            label=_(u'accounts:SignupForm:city:label'),
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'accounts:SignupForm:city:placeholder'),
                }),
            )
    zip = forms.RegexField(
            max_length=5,
            label=_(u'accounts:SignupForm:zip:label'),
            widget=forms.TextInput(attrs={
                u'placeholder': _(u'accounts:SignupForm:zip:placeholder'),
                }),
            regex=r'^\d{5}$',
            )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        # Defined here and not in the class definition above to make sure the field is places after
        # allauth email and password fields.
        self.fields[u'agreement'] = forms.BooleanField(
            label=_(u'accounts:SignupForm:agreement:label'),
            required=True,
            )


    def signup(self, request, user):
        user.first_name = self.cleaned_data[u'first_name']
        user.last_name = self.cleaned_data[u'last_name']
        user.save()
        user.profile.street = self.cleaned_data[u'street']
        user.profile.city = self.cleaned_data[u'city']
        user.profile.zip = self.cleaned_data[u'zip']
        user.profile.save()

class SettingsForm(forms.Form):

    anonymize_inforequests = forms.BooleanField(
            label=_(u'accounts:SettingsForm:anonymize_inforequests:label'),
            required=False,
            )

    custom_anonymization = forms.BooleanField(
            label=_(u'accounts:SettingsForm:custom_anonymization:label'),
            required=False,
            help_text=_(u'accounts:SettingsForm:custom_anonymization:help_text'),
            widget=forms.CheckboxInput(attrs={
                u'class': u'pln-toggle-changed',
                u'data-container': u'form',
                u'data-hide-target-true': u'.form-group:has(.visible-if-true)',
            }),
            )

    custom_anonymized_strings = forms.CharField(
            label=_(u'accounts:SettingsForm:custom_anonymized_strings:label'),
            required=False,
            help_text=_(u'accounts:SettingsForm:custom_anonymized_strings:help_text'),
            widget=forms.Textarea(attrs={
                u'class': u'pln-autosize visible-if-true',
                u'cols': u'', u'rows': u'',
                }),
            )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        kwargs[u'initial'] = {
                u'anonymize_inforequests': user.profile.anonymize_inforequests,
                u'custom_anonymization': bool(self.user.profile.custom_anonymized_strings),
                u'custom_anonymized_strings': self.initial_custom_anonymized_strings(),
                }
        super(SettingsForm, self).__init__(*args, **kwargs)

    def save(self):
        profile = self.user.profile
        custom_anonymized_strings = self.user.profile.custom_anonymized_strings
        profile.anonymize_inforequests = self.cleaned_data[u'anonymize_inforequests']
        profile.custom_anonymized_strings = self.cleaned_data[u'custom_anonymized_strings']
        if custom_anonymized_strings != self.cleaned_data[u'custom_anonymized_strings']:
            AttachmentFinalization.objects.owned_by(self.user).delete()
            AttachmentAnonymization.objects.owned_by(self.user).delete()
            profile.save(update_fields=[u'anonymize_inforequests', u'custom_anonymized_strings'])
        else:
            profile.save(update_fields=[u'anonymize_inforequests'])

    def clean_custom_anonymized_strings(self):
        if self.cleaned_data[u'custom_anonymization'] is False:
            return None
        custom_anonymized_strings = self.cleaned_data[u'custom_anonymized_strings'].split(u'\n')
        sentences = []
        for sentence in custom_anonymized_strings:
            sentence = sentence.strip()
            if len(sentence) >= WORD_SIZE_MIN:
                sentences.append(sentence)
        if sentences == []:
            raise forms.ValidationError(_(u'accounts:SettingsForm:custom_anonymized_strings:Error'))
        return sentences

    def initial_custom_anonymized_strings(self):
        ret = self.user.profile.custom_anonymized_strings
        if ret is None:
            ret = (
                    self.user.first_name.split() +
                    self.user.last_name.split() +
                    [self.user.profile.street] +
                    [self.user.profile.city] +
                    [self.user.profile.zip]
                    )
        return u'\n'.join(ret)

