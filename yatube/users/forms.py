from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма для регистрации пользователя."""

    class Meta(UserCreationForm.Meta):
        """Ссылаемся на модель и выбираем нужные поля из модели."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
