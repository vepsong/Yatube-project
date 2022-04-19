from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTest(TestCase):
    """Проверка Views приложения about."""

    @classmethod
    def setUpClass(cls):
        """Создание пользователя."""
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_client = Client()

    def test_about_views_access(self):
        """Тест доступности генерируемых URL."""
        url_list = {
            # приложение about
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }

        for url, expected in url_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected)

    def test_about_views_templates(self):
        """Тест использованных шаблонов."""
        url_list = {
            # приложение about
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for url, expected in url_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, expected)
