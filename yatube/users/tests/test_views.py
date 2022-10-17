from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.auth_client = Client()

        self.auth_client.force_login(UsersViewsTests.user)

    def test_users_pages(self):
        """Соответствие URL-адресов шаблонам в Users"""

        pages_templates_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
