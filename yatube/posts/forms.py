from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Класс формы для создания публикаци."""

    def __init__(self, *args, **kwargs):
        """Изменение характеристик наследуемой модели."""
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Если хотите, выберите группу"

    class Meta:
        """Сбор необходимых полей из молели.

        model — ссылка на нужную модель
        fields — выбираем нужные поля
        widgets — добавляем виджеты (напр., размер полей и пр.)
        """

        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }


class CommentForm(forms.ModelForm):
    """Класс формы для создания комментария."""

    class Meta:
        """Сбор необходимых полей из молели.

        model — ссылка на нужную модель
        fields — выбираем нужные поля
        widgets — добавляем виджеты (напр., размер полей и пр.)
        """

        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }
