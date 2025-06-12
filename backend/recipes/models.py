from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

import core.constants as cnsts
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=cnsts.MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=cnsts.MAX_TAG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=cnsts.MAX_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=cnsts.MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель произведения."""

    name = models.CharField(
        'Название',
        max_length=cnsts.MAX_RECIPE_LENGTH
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(cnsts.MIN_TIME_QUANTITY),
            MaxValueValidator(cnsts.MAX_TIME_QUANTITY)
        )
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipes/images/'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиента в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(cnsts.MIN_TIME_QUANTITY),))

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='%(class)s_unique_recipe_ingredient'),
        )
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} — {self.amount} в "{self.recipe}"'


class BaseUserRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='users_%(class)s',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_%(class)ss',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user__username',)
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='%(class)s_unique_user_recipe'),
        )

    def __str__(self):
        return f'{self._meta.verbose_name}: {self.user} — {self.recipe}'


class Favorite(BaseUserRecipe):
    """Модель избранного."""

    class Meta(BaseUserRecipe.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(BaseUserRecipe):
    """Модель списка покупок."""

    class Meta(BaseUserRecipe.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
