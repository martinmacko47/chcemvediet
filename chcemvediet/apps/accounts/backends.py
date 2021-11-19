from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.backends import ModelBackend
from django.core.urlresolvers import resolve, Resolver404

from poleno.utils.http import get_request


class AdminLoginAsBackendMixin(ModelBackend):

    def is_admin_path(self, path):
        return resolve(path).namespace == u'admin'

    def get_user(self, user_id):
        request = get_request()
        user = super(AdminLoginAsBackendMixin, self).get_user(user_id)
        if request is None:
            return user
        try:
            resolve(request.path)
        except Resolver404:
            return user
        admin_login_as = request.session.get(u'admin_login_as')
        if user and user.is_staff and not self.is_admin_path(request.path) and admin_login_as:
            return super(AdminLoginAsBackendMixin, self).get_user(admin_login_as) or user
        return user

class DjangoModelBackendWithAdminLoginAs(AdminLoginAsBackendMixin, ModelBackend):
    pass

class AllauthAuthenticationBackendWithAdminLoginAs(AdminLoginAsBackendMixin, AuthenticationBackend):
    pass
