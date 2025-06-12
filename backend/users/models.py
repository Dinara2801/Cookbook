from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models

import core.constants as cnsts


class User(AbstractUser):
    """Модель пользователя с преопределенным полем email."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=cnsts.LIMIT_FIRST_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=cnsts.LIMIT_FIRST_NAME
    )
    avatar = models.ImageField(
        'Фото',
        upload_to='users/images/',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            ),
        )
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        return f'{self.author.username} подписан на {self.user.username}'
