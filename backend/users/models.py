from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

USER, GUEST, ADMIN = 'user', 'guest', 'admin'
ROLES_CHOICES = [
    (USER, 'Пользователь'),
    (GUEST, 'Гость'),
    (ADMIN, 'Админ'),
]


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        unique=False
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        unique=False
    )

    role = models.CharField(
        max_length=16,
        choices=ROLES_CHOICES,
        default=USER
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password',
    ]

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    @property
    def is_guest(self):
        return self.role == GUEST

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError('На самого себя нельзя подписываться')

    class Meta:
        verbose_name = 'Подписка',
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe_user_author'
            )
        ]
