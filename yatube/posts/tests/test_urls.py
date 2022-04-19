from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTest(TestCase):
    """Проверка доступности URL, шаблонов, редиректов приложения posts."""

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

        # создание тестовой группы
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        # создание тестового поста
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_post',
            pk=1,
        )

# блок с тестами доступности URL
# для пользователей с различными уровнями доступа

    def test_posts_public_URL(self):
        """Проверяем публ. URL для незарег. польз."""
        public_URL_list = {
            # главная страница
            '/': HTTPStatus.OK,
            # личная страница автора
            f'/profile/{self.author.username}/': HTTPStatus.OK,
            # список групп
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            # просмотр и редактирование постов
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            # панель администратора
            '/admin/': HTTPStatus.FOUND,
            # создание поста
            '/create/': HTTPStatus.FOUND,
            # список подписок
            '/follow/': HTTPStatus.FOUND,
            # несуществующая страница
            '/test/non-existent/': HTTPStatus.NOT_FOUND,
        }

        for url, expected in public_URL_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected)

    def test_posts_private_URL(self):
        """Проверяем доступность приватных URL для зарег. польз."""
        private_URL_list = {
            '/admin/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
        }

        for url, expected in private_URL_list.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertEqual(response.status_code, expected)

    def test_admin_panel(self):
        """Проверяем superuser."""
        # проверка, что superuser может попасть в панель администратора
        response = self.authorized_superuser.get('/admin/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_author_post_edit(self):
        """Проверяем редактирование поста не автором."""
        # проверка, может ли не автор редактировать пост
        response = self.authorized_not_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

# блок с тестами редиректов

    def test_posts_public_redirect(self):
        """Проверяем редиректы незарег. пользователя."""
        redirect = '/auth/login/?next='
        public_redirect_list = {
            '/create/': redirect,
            f'/posts/{self.post.pk}/edit/': redirect,
            '/follow/': redirect,
        }

        for url, expected in public_redirect_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                expectedlink = expected + url
                self.assertRedirects(response, expectedlink)

    def test_not_author_post_edit_redirect(self):
        """Проверяем редирект при edit не автора поста."""
        # проверка редиректа, если не автор поста попробует edit
        response = self.authorized_not_author.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

# блок с тестами используемых шаблонов
    def test_posts_templates(self):
        """Тест используемых шаблоны."""
        template_list = {
            # главная страница
            '/': 'posts/index.html',
            # приложение posts
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for url, expected in template_list.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, expected)
