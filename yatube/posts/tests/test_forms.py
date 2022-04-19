import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

# создаем директорию TEMP_MEDIA_ROOT для
# хранения тестовых медиафайлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    """Тест формы создания / редактирования поста."""

    @classmethod
    def setUpClass(cls):
        """Инициализация тестовых данных."""
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )

        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )

        cls.authorized_not_author = Client()
        cls.authorized_not_author.force_login(cls.not_author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_description'
        )

        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text_1',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет
        # директорию TEMP_MEDIA_ROOT и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма PostForm создает запись в БД.

        Проверяем редирект и увеличение кол-ва постов в БД
        """
        posts_count = Post.objects.count()

        # Для тестирования загрузки изображений
        # создаем рандомное изображение
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        # загружаем изображение
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'test_text_2',
            'author': self.author,
            'group': self.group.pk,
            'image': uploaded
        }

        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author.username}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Тест, что отредактированный пост сохранился в БД.

        Проверка редиректа, сохранение измененного поста в БД,
        отсутствие новых записей в БД при редактировании поста.
        """
        posts_count = Post.objects.count()

        small_gif2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        # # загружаем изображение
        uploaded2 = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif2,
            content_type='image/gif'
        )

        form_data_edit = {
            'text': 'test_text_3',
            'author': self.author,
            'group': self.group.pk,
            'image': uploaded2,
        }

        response_edit = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            follow=True
        )

        self.assertRedirects(response_edit, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))

        self.assertTrue(
            Post.objects.filter(
                author=form_data_edit['author'],
                group=form_data_edit['group'],
                text=form_data_edit['text'],
                pk=self.post.pk,
                image=f'posts/{uploaded2.name}'
            ).exists()
        )

        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_edit_post_not_permitted_users(self):
        """Тест на добавление / ред. постов не уполномоченным user'ом.

        Неавторизованный user не может создать / ред. пост.
        Авторизованный user, НЕ автор поста не может ред. этот пост.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test_text_4',
            'author': self.author,
            'group': self.group.pk
        }
        form_data_edit = {
            'text': 'test_text_5',
            'author': self.author,
            'group': self.group.pk
        }

        view_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        ]
        data_list = [form_data, form_data_edit]
        # добавляем / редактируем пост от неавторизованного пользователя
        for url in view_list:
            for form_data in data_list:
                self.guest_client.post(url, form_data)
        # проверяем, что пост не добавился в БД
        self.assertEqual(Post.objects.count(), posts_count)
        # редактируем пост авторизованным пользователем НЕ автором поста
        self.authorized_not_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            form_data
        )
        # проверяем, что в БД не появилось поста с измененными данными
        self.assertFalse(
            Post.objects.filter(
                author=form_data_edit['author'],
                group=form_data_edit['group'],
                text=form_data_edit['text'],
                pk=self.post.pk
            ).exists()
        )

    def test_create_comment(self):
        """Валидная форма CommentForm создает запись в БД.

        Проверяем редирект и увеличение кол-ва комментариев в БД
        """
        comment_count = Comment.objects.count()

        form_data = {
            'text': 'test_comment_01',
            'author': self.author,
        }

        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )

        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_comment_not_permitted_users(self):
        """Тест на добавление комментариев не уполномоченным user'ом.

        Неавторизованный user не может создать комментарий.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'test_comment_01',
            'author': self.author,
        }
        view_list = [
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        ]
        data_list = [form_data]

        # добавляем  комментарий от неавторизованного пользователя
        for url in view_list:
            for form_data in data_list:
                self.guest_client.post(url, form_data)
        # проверяем, что комментарий не добавился в БД
        self.assertEqual(Comment.objects.count(), comment_count)
