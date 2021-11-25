# vim: expandtab
# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from poleno.utils.admin_login_as import AdminLoginAsAdminMixin
from poleno.utils.admin import simple_list_filter_factory, admin_obj_format
from poleno.utils.misc import decorate

from .models import Profile


class ProfileAdminForm(forms.ModelForm):

    def clean_custom_anonymized_strings(self):
        custom_anonymized_strings = self.cleaned_data[u'custom_anonymized_strings']
        if custom_anonymized_strings is None:
            return None
        if type(custom_anonymized_strings) != list:
            raise ValidationError(u'JSON must be an array of strings')
        for line in custom_anonymized_strings:
            if type(line) != unicode:
                raise ValidationError(u'JSON must be an array of strings')
        return custom_anonymized_strings

@admin.register(Profile, site=admin.site)
class ProfileAdmin(AdminLoginAsAdminMixin, admin.ModelAdmin):
    form = ProfileAdminForm
    date_hierarchy = None
    list_display = [
            u'id',
            decorate(
                lambda o: admin_obj_format(o.user,
                    u'{obj.first_name} {obj.last_name} <{obj.email}>'),
                short_description=u'User',
                admin_order_field=u'user__email',
                ),
            u'street',
            u'city',
            u'zip',
            u'anonymize_inforequests',
            decorate(
                lambda o: o.undecided_emails_count,
                short_description=u'Undecided E-mails',
                admin_order_field=u'undecided_emails_count',
                ),
            decorate(
                lambda o: admin_obj_format(o, u'Log in', link=u'login_as'),
                short_description=u'Login As',
                ),
            ]
    list_filter = [
            u'anonymize_inforequests',
            simple_list_filter_factory(u'Undecided E-mail', u'undecided', [
                (u'1', u'With', lambda qs: qs.filter(undecided_emails_count__gt=0)),
                (u'0', u'Without', lambda qs: qs.filter(undecided_emails_count=0)),
                ]),
            ]
    search_fields = [
            u'=id',
            u'user__first_name',
            u'user__last_name',
            u'user__email',
            u'street',
            u'city',
            u'zip',
            ]
    ordering = [
            u'id',
            ]
    exclude = [
            ]
    readonly_fields = [
            ]
    raw_id_fields = [
            u'user',
            ]
    inlines = [
            ]
    LOGIN_AS_REDIRECT_VIEWNAME = u'inforequests:mine'

    def get_queryset(self, request):
        queryset = super(ProfileAdmin, self).get_queryset(request)
        queryset = queryset.select_related(u'user')
        queryset = queryset.select_undecided_emails_count()
        return queryset
