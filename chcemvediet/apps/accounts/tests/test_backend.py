import mock

from django.conf.urls import patterns, url
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.test.utils import override_settings

from poleno.utils.http import _local


class AdminLoginAsBackendTest(TestCase):

    def mock_view(request):
        return HttpResponse()

    def set_admin_login_as_attribute_view(request, id):
        request.session[u'admin_login_as'] = id
        return HttpResponse()

    urls = tuple(patterns(u'',
        url(r'^$', mock_view),
        url(r'^(.+)/login-as/$', set_admin_login_as_attribute_view),
    ))

    def create_users(self):
        self.user = User.objects.create_user(
                username=u'user',
                email=u'user@example.com',
                password=u'test',
                )
        self.superuser = User.objects.create_superuser(
                username=u'superuser',
                email=u'superuser@example.com',
                password=u'test',
                )

    def setUp(self):
        self.settings_override = override_settings(
            AUTHENTICATION_BACKENDS=(u'chcemvediet.apps.accounts.backends.AdminLoginAsBackend',),
            PASSWORD_HASHERS=(u'django.contrib.auth.hashers.MD5PasswordHasher',),
        )
        self.settings_override.enable()
        self.create_users()

    def tearDown(self):
        self.settings_override.disable()


    def test_get_user_returns_anonymous_user(self):
        response = self.client.get(u'/')
        request = response.wsgi_request
        user = get_user(request)
        self.assertIsNotNone(user)
        self.assertTrue(user.is_anonymous())

    def test_get_user_returns_logged_non_admin_user(self):
        self.assertTrue(self.client.login(
                username=self.user.username, password=u'test'
        ))
        response = self.client.get(u'/')
        request = response.wsgi_request
        _local.request = request
        user = get_user(request)
        self.assertEqual(user, self.user)

    def test_get_user_returns_logged_admin_user_on_admin_page(self):
        with mock.patch(u'chcemvediet.apps.accounts.backends.AdminLoginAsBackend.is_admin_path', return_value=True):
            self.assertTrue(self.client.login(
                    username=self.superuser.username, password=u'test'
            ))
            response = self.client.get(u'/')
            request = response.wsgi_request
            _local.request = request
            user = get_user(request)
            self.assertEqual(user, self.superuser)

    def test_get_user_returns_logged_admin_user_if_admin_login_as_attribute_is_not_set(self):
        with mock.patch(u'chcemvediet.apps.accounts.backends.AdminLoginAsBackend.is_admin_path', return_value=False):
            self.assertTrue(self.client.login(
                    username=self.superuser.username, password=u'test'
            ))
            response = self.client.get(u'/')
            request = response.wsgi_request
            _local.request = request
            user = get_user(request)
            self.assertEqual(user, self.superuser)

    def test_get_user_returns_selected_user_if_admin_login_as_attribute_is_set(self):
        with mock.patch(u'chcemvediet.apps.accounts.backends.AdminLoginAsBackend.is_admin_path', return_value=False):
            self.assertTrue(self.client.login(
                    username=self.superuser.username, password=u'test'
            ))
            self.client.get(u'/{}/login-as/'.format(self.user.pk))
            response = self.client.get(u'/')
            request = response.wsgi_request
            _local.request = request
            user = get_user(request)
            self.assertEqual(user, self.user)
