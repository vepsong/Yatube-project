from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Создаем тестового пользователя, экз. модели group, comment."""

    @classmethod
    def setUpClass(cls):
        """Инициализация тестовых данных."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый очень длинный пост' * 3,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый очень длинный комментарий' * 3,
            post_id=cls.post.pk
        )

    def test_models_have_correct_object_names(self):
        """__str__ Post (text[:15]), Comment (text[:15]), Group(title)."""
        exp_obj_name = self.group.title
        exp_obj_text_post = self.post.text[:15]
        exp_obj_text_comment = self.comment.text[:15]

        self.assertEqual(exp_obj_name, str(self.group))

        self.assertEqual(exp_obj_text_post, str(self.post))

        self.assertEqual(exp_obj_text_comment, str(self.comment))

    def test_verbose_name(self):
        """Проверка verbose_name."""
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Проверка help_text."""
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)
