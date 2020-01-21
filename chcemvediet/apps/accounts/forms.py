# vim: expandtab
# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


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

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SettingsForm, self).__init__(*args, **kwargs)

    def save(self):
        self.user.profile.anonymize_inforequests = self.cleaned_data[u'anonymize_inforequests']
        self.user.profile.save(update_fields=[u'anonymize_inforequests'])
