from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создание пользователя
        cls.user = User.objects.create_user(username='test_user')
        cls.user_not_author = User.objects.create_user(
            username='test_user_not_author'
        )
        # Создание группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client_not_author = Client()

        self.auth_client.force_login(PostsURLTests.user)
        self.auth_client_not_author.force_login(PostsURLTests.user_not_author)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_urls(self):
        """Проверка корректности URL"""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_names = [
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post.pk}/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client.get(address)

                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_post_edit_url(self):
        """Проверка доступности страницы редактирования поста"""
        post = PostsURLTests.post
        address = f'/posts/{post.pk}/edit/'
        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)
        auth_not_author_response = (
            self.auth_client_not_author.get(address)
        )

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{post.pk}/edit/'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')
        self.assertEqual(
            auth_not_author_response.url,
            f'/posts/{post.pk}/'
        )

    def test_create_post_url(self):
        """Проверка доступности страницы создания поста"""
        address = f'{"/create/"}'
        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'{"/auth/login/?next=/create/"}'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_404_error_return_for_unexisting_page(self):
        """Проверка возврата ошибки 404"""
        address = f'{"/fake_page/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertEqual(guest_response.reason_phrase, 'Not Found')
        self.assertEqual(auth_response.reason_phrase, 'Not Found')

    def test_template(self):
        """Проверка соответствия URL шаблонам"""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)
