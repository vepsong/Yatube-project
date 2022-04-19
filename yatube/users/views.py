from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Класс регистрации пользователя.

    form_class — ссылаемся на созданный класс в users/forms.py
    success_url — redirect после успешной регитрации
    template_name — адрес шаблона html
    """

    form_class = CreationForm
    success_url = reverse_lazy('posts:main_page')
    template_name = 'users/signup.html'
