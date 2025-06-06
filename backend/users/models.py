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
        upload_to='users/images/'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_user_following'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        )
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.following.username} подписан на {self.user.username}'
