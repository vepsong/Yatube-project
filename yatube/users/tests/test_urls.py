from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTest(TestCase):
    """Проверка доступности URL, шаблонов, редиректов в приложении Users."""

    @classmethod
    def setUpClass(cls):
        """Создание тест. автор. и неавт. клиента."""
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_client = Client()

        # создаем автора(пользователя)
        cls.author = User.objects.create_user(
            username='test_author'
        )
        # авторизованный пользователь
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

# блок с тестами доступности URL

    def test_users_public_URL(self):
        """Проверяем публичные URL для незарег. польз."""
        public_URL_list = {
            # auth
            '/auth/signup/': 200,
            '/auth/login/': 200,
        }

        for url, expected in public_URL_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected)

    # def test_auth_redirect(self):
    #     """Проверяем auth редиректы."""
    #     auth_redirect_list = {
    #         '/auth/signup/': '/',
    #     }

    #     for url, expected in auth_redirect_list.items():
    #         with self.subTest(url=url):
    #             response = self.authorized_author.get(url, follow=True)
    #             self.assertRedirects(response, expected)

# блок с тестами используемых шаблонов
    def test_users_templates(self):
        """Тест используемых шаблоны."""
        template_list = {
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
        }

        for url, expected in template_list.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, expected)
