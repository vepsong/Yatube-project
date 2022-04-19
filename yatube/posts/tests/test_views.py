import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

# создаем директорию TEMP_MEDIA_ROOT для
# хранения тестовых медиафайлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    """Проверка Views приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создание пользователей."""
        super().setUpClass()

        # Неавторизованный клиент
        cls.guest_client = Client()

        # создаем автора(пользователя) владельца публикации в БД
        cls.author = User.objects.create_user(
            username='test_author'
        )
        # авторизованный пользователь, автор публикации
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        # создаем автора(пользователя) НЕ владельца публикации в БД
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        # авторизованный пользователь, НЕ автор публикации
        cls.authorized_not_author = Client()
        cls.authorized_not_author.force_login(cls.not_author)

        # создаем superuser'a в БД
        cls.superuser = User.objects.create_superuser(
            username='test_superuser',
            email='test_email',
            password='test_password',
        )
        # авторизуем superuser'a
        cls.authorized_superuser = Client()
        cls.authorized_superuser.force_login(cls.superuser)

        # создание тестовой группы N1
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

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

        # создание тестового поста
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_post',
            group=cls.group,
            pk=1,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет
        # директорию TEMP_MEDIA_ROOT и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_views_access(self):
        """Тест используемых шаблонов."""
        url_templates = {
            # приложение posts
            reverse('posts:main_page'): 'posts/index.html',
            reverse('posts:group_post',
                    kwargs={'slug': self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}):
                        'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}):
                        'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

        for view, template in url_templates.items():
            with self.subTest(view=view):
                response = self.authorized_author.get(view)
                self.assertTemplateUsed(response, template)

    def test_posts_post_context(self):
        """Проверка контекста page_obj приложения posts.

        тестируем posts:main_page, posts:group_post, posts:profile
        """
        templates = [
            reverse('posts:main_page'),
            reverse('posts:group_post', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.author.username})
        ]
        for url in templates:
            response = self.authorized_author.get(url)
            post = response.context['page_obj'][0]
            context_post_detail = {
                post.text: self.post.text,
                post.pub_date: self.post.pub_date,
                post.author: self.post.author,
                post.group: self.post.group,
                post.image: self.post.image
            }
            for context, res in context_post_detail.items():
                with self.subTest(context=context):
                    self.assertEqual(context, res)

    def test_posts_group_context(self):
        """Проверка контекста group приложения posts.

        тестируем posts:group_post
        """
        # несмотря на проверку всего лишь одной view-функции, использую
        # список и цикл. Это сделано, если в дальнейшем добавятся view-функции
        # с контекстом group и их можно будет быстро встроить в тест.
        templates = [
            reverse('posts:group_post', kwargs={'slug': self.group.slug}),
        ]
        for i in templates:
            response = self.authorized_author.get(i)
            group = response.context['group']
            context_group_list = {
                group.title: self.group.title,
                group.slug: self.group.slug,
                group.description: self.group.description
            }
            for context, res in context_group_list.items():
                with self.subTest(context=context):
                    self.assertEqual(context, res)

    def test_posts_group_context(self):
        """Проверка контекста author приложения posts.

        тестируем posts:profile
        """
        # несмотря на проверку всего лишь одной view-функции, использую
        # список и цикл. Это сделано, если в дальнейшем добавятся view-функции
        # с контекстом author и их можно будет быстро встроить в тест.
        templates = [
            reverse(
                'posts:profile', kwargs={'username': self.author.username}),
        ]
        for i in templates:
            response = self.authorized_author.get(i)
            author = response.context['author']
            context_group_list = {
                author.username: self.author.username
            }
            for context, res in context_group_list.items():
                with self.subTest(context=context):
                    self.assertEqual(context, res)

    def test_posts_post_context(self):
        """Проверка context post приложения posts."""
        # несмотря на проверку всего лишь одной view-функции, использую
        # список и цикл. Это сделано, если в дальнейшем добавятся view-функции
        # с контекстом post и их можно будет быстро встроить в тест.

        templates = [
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        ]
        for i in templates:
            response = self.authorized_author.get(i)
            post_detail = response.context['post']
            context_post_detail = {
                post_detail.text: self.post.text,
                post_detail.pub_date: self.post.pub_date,
                post_detail.author: self.post.author,
                post_detail.group: self.post.group,
                post_detail.image: self.post.image,
            }
            for context, res in context_post_detail.items():
                with self.subTest(context=context):
                    self.assertEqual(context, res)

    def test_comment_create_context(self):
        """Проверка context comment_create."""
        response = self.authorized_author.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_create_context(self):
        """Проверка context страницы post_create."""
        response = self.authorized_author.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_correct_group(self):
        """Проверяем что пост не попал в другую группу."""
        self.group2 = Group.objects.create(
            title='test_group2',
            slug='test_slug2',
            description='test_description2',
        )
        # при инициализации данных был создан пост с группой №1
        # соответственно, при переходе на страницу группы №2
        # там не должно быть постов
        response = self.authorized_author.get(
            reverse('posts:group_post', kwargs={'slug': self.group2.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_main_page(self):
        """Тест cache главной стр. приложения post."""
        response = self.authorized_author.get(
            reverse('posts:main_page')).content
        # создание тестового поста N2
        Post.objects.create(
            author=self.author,
            text='test_post_2',
            group=self.group,
        )
        response_cache = self.authorized_author.get(
            reverse('posts:main_page')).content

        self.assertEqual(response, response_cache)

        cache.clear()

        response_cache_clear = self.authorized_author.get(
            reverse('posts:main_page')).content

        self.assertNotEqual(response, response_cache_clear)


class PaginatorViewsTest(TestCase):
    """Тест paginator приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Тестовые посты и группы."""
        super().setUpClass()
        # создаем автора(пользователя) владельца публикации в БД
        cls.author = User.objects.create_user(
            username='test_paginator_author'
        )
        # авторизованный пользователь, автор публикации
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        # создание тестовой группы
        cls.group = Group.objects.create(
            title='test_paginator_group',
            slug='test_paginator_group_slug',
            description='test_paginator_group_description',
        )

        # создаем 13 тестовых записей для тестирования
        # первой и второй страницы паджинатора
        for i in range(13):
            Post.objects.create(
                author=cls.author,
                text=f'test_paginator_text_post_N_{i + 1}',
                group=cls.group,
            )

    def test_paginator_posts(self):
        """Тест паджинатора приложения posts.

        тестируем posts:main_page, posts:group_post, posts:profile
        """
        templates = [
            reverse('posts:main_page'),
            reverse('posts:group_post', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author.username})
        ]

        for url in templates:
            with self.subTest(templates=url):
                response1 = self.authorized_author.get(url)
                response2 = self.authorized_author.get(
                    url + '?page=2')
                # на первой странице выводится 10 записей
                # p.s. число 10 берется из указанных в viwes.py
                # настройках паджинатора
                self.assertEqual(
                    len(response1.context['page_obj']), 10)
                # на второй странице выводится 3 записи
                self.assertEqual(
                    len(response2.context['page_obj']), 3)


class Follow_Unfollow_ViewsTest(TestCase):
    """Тест подписки/отписки от автора."""

    @classmethod
    def setUpClass(cls):
        """Создание пользователей."""
        super().setUpClass()

        # Неавторизованный пользователь
        cls.guest_client = Client()

        # создаем автора(пользователя) №1
        cls.author_01 = User.objects.create_user(
            username='test_author_01'
        )
        # авторизуем автора(пользователя) №1
        cls.authorized_author_01 = Client()
        cls.authorized_author_01.force_login(cls.author_01)

        # создаем автора(пользователя) №2
        cls.author_02 = User.objects.create_user(
            username='test_author_02'
        )
        # авторизуем автора(пользователя) №2
        cls.authorized_author_02 = Client()
        cls.authorized_author_02.force_login(cls.author_02)

        # создаем автора(пользователя) №3
        cls.author_03 = User.objects.create_user(
            username='test_author_03'
        )
        # авторизуем автора(пользователя) №3
        cls.authorized_author_03 = Client()
        cls.authorized_author_03.force_login(cls.author_03)

        # создание тестовой группы
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

        # создание тестового поста №1
        cls.post_01 = Post.objects.create(
            author=cls.author_01,
            text='test_post_01',
            group=cls.group,
            pk=1,
        )
        # создание тестового поста №2
        cls.post_02 = Post.objects.create(
            author=cls.author_02,
            text='test_post_02',
            group=cls.group,
            pk=2,
        )

    def test_follow(self):
        """Тест подписки на автора."""
        user = self.author_01
        auth_user = self.authorized_author_01
        author = self.author_02

        # от имени author_01 подписываемся на author_02
        auth_user.get(reverse(
            'posts:profile_follow', kwargs={'username': author.username}),
        )

        follower = Follow.objects.filter(
            user=user,
            author=author,
        ).exists()
        self.assertTrue(
            follower,
            'Не работает подписка'
        )

    def test_unfollow(self):
        """Тест отписки от автора."""
        user = self.author_01
        auth_user = self.authorized_author_01
        author = self.author_02

        # от имени author_01 отписываемся от author_02
        auth_user.get(reverse(
            'posts:profile_unfollow', kwargs={'username': author.username}),
        )

        follower = Follow.objects.filter(
            user=user,
            author=author,
        ).exists()
        self.assertFalse(
            follower,
            'Не работает отписка'
        )

    def test_follow_index(self):
        """Тест отображения постов в 'posts:follow_index'."""
        auth_user_01 = self.authorized_author_01
        auth_user_03 = self.authorized_author_03
        author = self.author_02
        # от имени author_01 и author_03 переходим
        # на страницу posts:follow_index и сравниваем количество постов
        # должно быть поровну, т.к. пользователи ни на кого не подписаны
        response_author_01 = auth_user_01.get(
            reverse('posts:follow_index')
        )

        response_author_03 = auth_user_03.get(
            reverse('posts:follow_index')
        )

        self.assertEqual(
            len(response_author_01.context['page_obj']),
            len(response_author_03.context['page_obj']),
        )

        # от имени author_01 подписываемся на author_02
        auth_user_01.get(reverse(
            'posts:profile_follow', kwargs={'username': author.username}),
        )

        # от имени author_01 и author_03 переходим
        # на страницу posts:follow_index и сравниваем количество постов
        # должно быть НЕ поровну, т.к. author_01 подписан на author_02

        response_author_01 = auth_user_01.get(
            reverse('posts:follow_index')
        )

        response_author_03 = auth_user_03.get(
            reverse('posts:follow_index')
        )

        self.assertNotEqual(
            len(response_author_01.context['page_obj']),
            len(response_author_03.context['page_obj']),
        )

        # от имени author_01 отписываемся от author_02
        auth_user_01.get(reverse(
            'posts:profile_unfollow', kwargs={'username': author.username}),
        )

        # от имени author_01 и author_03 переходим
        # на страницу posts:follow_index и сравниваем количество постов
        # должно быть поровну, т.к. пользователи ни на кого не подписаны
        response_author_01 = auth_user_01.get(
            reverse('posts:follow_index')
        )

        response_author_03 = auth_user_03.get(
            reverse('posts:follow_index')
        )

        self.assertEqual(
            len(response_author_01.context['page_obj']),
            len(response_author_03.context['page_obj']),
        )
