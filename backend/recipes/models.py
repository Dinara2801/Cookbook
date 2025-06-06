from django.core.validators import MinValueValidator
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
        return self.name[:cnsts.MAX_STR_LENGTH]


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
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:cnsts.MAX_STR_LENGTH]


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
        validators=(MinValueValidator(cnsts.MIN_TIME_QUANTITY),)
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
        related_name='recipes'
    )

    class Meta:
        default_related_name = 'title'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name[:cnsts.MAX_STR_LENGTH]


class IngredientInRecipe(models.Model):
    """Модель ингредиента в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
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
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class BaseFavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='users_%(class)s'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_%(class)ss'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='%(class)s_unique_user_recipe'),
        )

    def __str__(self):
        return f'{self.user} — {self.recipe}'


class Favorite(BaseFavoriteShoppingCart):
    """Модель избранного."""

    class Meta(BaseFavoriteShoppingCart.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(BaseFavoriteShoppingCart):
    """Модель списка покупок."""

    class Meta(BaseFavoriteShoppingCart.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
