from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()

    def test_user_create(self):
        """Запись в User."""
        users_count = User.objects.count()

        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'test_user_1',
            'email': 'test_user@yandex.ru',
            'password1': '87654321!A',
            'password2': '87654321!A',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Test',
                last_name='User',
                username='test_user_1',
                email='test_user@yandex.ru',
            ).exists()
        )
