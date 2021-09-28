from django.contrib.auth.backends import ModelBackend
from django.core.urlresolvers import resolve

from poleno.utils.http import get_request


class AdminLoginAsBackend(ModelBackend):

    def is_admin_path(self, path):
        return resolve(path).func.__module__ in [
                u'django.contrib.admin.options',
                u'django.contrib.admin.sites',
                u'adminplus.sites',
                u'chcemvediet.apps.accounts.admin',
                ]

    def get_user(self, user_id):
        request = get_request()
        admin_login_as = request.session.get(u'admin_login_as')
        user = super(AdminLoginAsBackend, self).get_user(user_id)
        admin_login_as_user = super(AdminLoginAsBackend, self).get_user(admin_login_as)
        if user and user.is_staff and not self.is_admin_path(request.path) and admin_login_as:
            return admin_login_as_user
        return user
