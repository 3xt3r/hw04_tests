from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(UsersURLTests.user)

    def test_correct_urls(self):
        """Проверка страниц"""

        url_names = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/logout/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client.get(address)
                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_correct_template(self):
        """Проверка шаблонов"""

        url_templates_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)
