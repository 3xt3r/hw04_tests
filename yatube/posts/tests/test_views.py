from time import sleep
from yatube.settings import NUMBER_OF_POSTS
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()

TEST_POST_TEXT = 'Тестовый пост'
TEST_POSTS_OFFSET = NUMBER_OF_POSTS - 1


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )

        for i in range(NUMBER_OF_POSTS + TEST_POSTS_OFFSET):
            Post.objects.create(
                author=cls.user,
                group=cls.group2,
                text=f'Тестовый пост №{i+1}',
            )
            sleep(0.01)

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEST_POST_TEXT,
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostsViewsTests.user)

    def test_correct_templates(self):
        """Проверка соответствия url шаблонам"""
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        urls_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}
            ): 'posts/create_post.html',
        }

        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка контекста шаблона index"""
        response = self.auth_client.get(reverse('posts:index'))

        context_post = response.context['page_obj'][0]
        post_author = context_post.author
        post_group = context_post.group
        post_text = context_post.text

        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group)
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        group = PostsViewsTests.group
        response = self.auth_client.get(
            reverse('posts:group_posts', kwargs={'slug': group.slug})
        )

        context_post = response.context['page_obj'][0]
        post_author = context_post.author
        post_group = context_post.group
        post_text = context_post.text
        context_group = response.context['group'].title

        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group)
        self.assertEqual(context_group, self.group.title)
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        posts_count = Post.objects.count()
        user = PostsViewsTests.user
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': user.username})
        )

        context_post = response.context['page_obj'][0]
        post_author = context_post.author
        post_group = context_post.group
        post_text = context_post.text
        context_author = response.context['author'].username
        context_posts_count = response.context['posts_count']

        self.assertEqual(post_author, self.user)
        self.assertEqual(context_author, 'test_user')
        self.assertEqual(post_group, self.group)
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(context_posts_count, posts_count)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        posts_count = Post.objects.count()
        post = PostsViewsTests.post
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.pk})
        )

        context_post = response.context['post_info']
        post_author = context_post.author
        post_group = context_post.group
        post_text = context_post.text
        context_posts_count = response.context['posts_count']

        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, self.group)
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(context_posts_count, posts_count)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post (create) сформирован с правильным контекстом"""
        response = self.auth_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post (edit) сформирован с правильным контекстом"""
        post = PostsViewsTests.post
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        context_post_id = response.context['post_id']

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(
            context_post_id,
            NUMBER_OF_POSTS
            + TEST_POSTS_OFFSET
            + 1)

    def test_post_correct_appear(self):
        """Проверка созданного поста"""
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        ]

        for page in pages_names:
            with self.subTest(page=page):
                response = self.auth_client.get(page)
                context_post = response.context['page_obj'][0]

                self.assertEqual(context_post, post)

    def test_post_correct_not_appear(self):
        ("""Проверка, что созданный пост не появляется в группе """
         """к которой он не принадлежит.""")
        group2 = PostsViewsTests.group2
        post = PostsViewsTests.post
        page = reverse('posts:group_posts', kwargs={'slug': group2.slug})

        response = self.auth_client.get(page)
        context_post = response.context['page_obj'][0]

        self.assertNotEqual(context_post, post)


class TestPaginator(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='authorized')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        post: list = []

        for i in range(NUMBER_OF_POSTS + TEST_POSTS_OFFSET):
            post.append(Post(text=f'{"Тестовый текст"}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(post)

    def test_posts_pages_paginator(self):

        urls_page2posts_names = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }

        for page in urls_page2posts_names:
            response1 = self.authorized_client.get(page)
            response2 = self.authorized_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])

            self.assertEqual(count_posts1,
                             NUMBER_OF_POSTS)
            self.assertEqual(count_posts2,
                             TEST_POSTS_OFFSET)
