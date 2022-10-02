from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Наименование ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет в теге',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        ordering =['name',]
        verbose_name = 'Тег'

    def __str__(self):
        return self.name
