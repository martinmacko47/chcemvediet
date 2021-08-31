from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.core.urlresolvers import resolve

from poleno.utils.http import get_request


class AdminLoginAsBackend(ModelBackend):

    def is_admin_path(self, path):
        return resolve(path).func.__module__ in [
                u'django.contrib.admin.options',
                u'django.contrib.admin.sites',
                u'adminplus.sites',
                ]

    def get_user(self, user_id):
        user = super(AdminLoginAsBackend, self).get_user(user_id)
        request = get_request()
        admin_login_as = request.session.get(u'admin_login_as')

        if not user:
            return None

        if user.is_staff:
            request.session[u'admin_login_as'] = user.id

        if self.is_admin_path(request.path) and not user.is_staff and admin_login_as:
            admin_user = super(AdminLoginAsBackend, self).get_user(admin_login_as)
            if admin_user:
                if not hasattr(admin_user, u'backend'):
                    admin_user.backend = u'poleno.utils.backends.AdminLoginAsBackend'
                login(request, admin_user)
                return admin_user
        return user
