from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from poleno.utils.urls import reverse


class AdminLoginAsBackend(TestCase):

    def create_users(self):
        self.user1 = User.objects.create_user(
                username=u'user1',
                email=u'user1@example.com',
                password=u'test',
                )
        self.user2 = User.objects.create_user(
                username=u'user2',
                email=u'user2@example.com',
                password=u'test',
                )
        self.superuser1 = User.objects.create_superuser(
                username=u'superuser1',
                email=u'superuser1@example.com',
                password=u'test',
                )
        self.superuser2 = User.objects.create_superuser(
            username=u'superuser2',
            email=u'superuser2@example.com',
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


    def test_multiple_requests(self):
        self.assertTrue(self.client.login(
            username=self.superuser1.username, password=u'test'
        ))
        url1 = reverse(u'admin:accounts_profile_login_as', args=(self.user1.pk,))
        url2 = reverse(u'admin:accounts_profile_login_as', args=(self.user2.pk,))
        expected_url = reverse(u'inforequests:mine')
        self.assertRedirects(self.client.get(url1, follow=True), expected_url)
        self.assertEqual(self.client.session[u'_auth_user_id'], self.user1.pk)
        self.assertRedirects(self.client.get(url2, follow=True), expected_url)
        self.assertEqual(self.client.session[u'_auth_user_id'], self.user2.pk)

    def test_logging_back_admin(self):
        self.client.login(username=self.superuser1.username, password=u'test')
        url = reverse(u'admin:accounts_profile_login_as', args=(self.user1.pk,))
        self.client.get(url, follow=True)
        self.assertEqual(self.client.session[u'_auth_user_id'], self.user1.pk)
        response = self.client.get(reverse(u'admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, u'adminplus/index.html')
        self.assertEqual(self.client.session[u'_auth_user_id'], self.superuser1.pk)

    def test_staff_user_login_as_other_staff_user(self):
        self.client.login(username=self.superuser1.username, password=u'test')
        self.assertEqual(self.client.session[u'_auth_user_id'], self.superuser1.pk)
        url = reverse(u'admin:accounts_profile_login_as', args=(self.superuser2.pk,))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse(u'inforequests:mine'))
        self.assertEqual(self.client.session[u'_auth_user_id'], self.superuser2.pk)
        response2 = self.client.get(reverse(u'admin:index'))
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, u'adminplus/index.html')
        self.assertEqual(self.client.session[u'_auth_user_id'], self.superuser2.pk)

    def test_login_to_non_existing_user(self):
        self.client.login(username=self.superuser1, password=u'test')
        url = reverse(u'admin:accounts_profile_login_as', args=(344,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
