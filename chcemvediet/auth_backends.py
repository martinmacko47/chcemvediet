from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth.backends import ModelBackend

from poleno.utils.admin_login_as import AdminLoginAsBackendMixin


class DjangoModelBackendWithAdminLoginAs(AdminLoginAsBackendMixin, ModelBackend):
    pass

class AllauthAuthenticationBackendWithAdminLoginAs(AdminLoginAsBackendMixin, AuthenticationBackend):
    pass
