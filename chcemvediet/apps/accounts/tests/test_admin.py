from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from poleno.utils.test import ViewTestCaseMixin
from poleno.utils.urls import reverse


class ProfileAdminTest(ViewTestCaseMixin, TestCase):
    u"""
    Tests ``login_as_view()`` view registered as "admin:accounts_profile_login_as".
    """

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
            PASSWORD_HASHERS=(u'django.contrib.auth.hashers.MD5PasswordHasher',),
        )
        self.settings_override.enable()
        self.create_users()

    def tearDown(self):
        self.settings_override.disable()


    def test_anonymous_user_is_redirected(self):
        url = reverse(u'admin:accounts_profile_login_as', args=(self.user.pk,))
        response = self.client.get(url, follow=True)
        expected_url = reverse(u'admin:login') + u'?next=' + url
        self.assertRedirects(response, expected_url)

    def test_staff_user_gets_inforequest_detail(self):
        self.assertTrue(self.client.login(
                username=self.superuser.username, password=u'test'
                ))
        url = reverse(u'admin:accounts_profile_login_as', args=(self.user.pk,))
        response = self.client.get(url, follow=True)
        expected_url = reverse(u'inforequests:mine')
        self.assertRedirects(response, expected_url)
        self.assertEqual(self.client.session[u'_auth_user_id'], self.user.id)
