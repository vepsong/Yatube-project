from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

from core.models import CreatedModel


User = get_user_model()


class Post(CreatedModel):
    """Модель поста."""

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'

    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        """Магический метод возврата текста поста."""
        return self.text[:15]


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        verbose_name='group_URL'
    )
    description = models.TextField()

    def __str__(self) -> str:
        """Магический метод возврата названия группы."""
        return self.title


class Comment(CreatedModel):
    """Модель комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите комментарий'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        """Магический метод возврата текста комментария."""
        return self.text[:15]


class Follow(CreatedModel):
    """Модель подписки на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        db_table = 'Follow'
        constraints = [UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follower'),
        ]
