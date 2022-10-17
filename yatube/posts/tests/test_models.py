from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_post_str(self):
        """Проверка __str__ у Post"""
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_post_verbose_name(self):
        """Проверка verbose_name у Post"""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                verbose_name = self.post._meta.get_field(value).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text у Post"""
        feild_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу', }
        for value, expected in feild_help_texts.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_str(self):
        """Проверка __str__ у Group."""
        self.assertEqual(self.group.title, str(self.group))
