from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTest(TestCase):
    """Проверка URL и шаблонов приложения about."""

    @classmethod
    def setUpClass(cls):
        """Создание тест. автор. и неавт. клиента."""
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_client = Client()

# блок с тестами доступности URL

    def test_about_public_URL(self):
        """Проверяем публ. URL для незарег. польз."""
        public_URL_list = {
            # о проекте
            '/about/author/': 200,
            '/about/tech/': 200,
        }

        for url, expected in public_URL_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected)

# блок с тестами используемых шаблонов
    def test_about_templates(self):
        """Тест используемых шаблоны."""
        template_list = {
            # приложение about
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for url, expected in template_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, expected)
