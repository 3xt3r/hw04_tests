from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEST_POST_TEXT = 'Тестовый пост'
TEST_POST_TEXT_2 = 'Изменённый тестовый пост'


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.auth_client = Client()

        self.auth_client.force_login(PostsFormsTests.user)

    def test_posts_create_post(self):
        """Запись в Post"""
        posts_count = Post.objects.count()

        form_data = {
            'text': TEST_POST_TEXT,
            'group': self.group.pk,
        }

        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_TEXT,
                group=self.group,
                author=self.user,
            ).exists()
        )

    def test_posts_edit_post(self):
        """Редактирует запись в Post"""
        posts_count = Post.objects.count()

        form_data = {
            'text': TEST_POST_TEXT_2,
            'group': self.group.pk,
        }

        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text,
            TEST_POST_TEXT_2
        )
