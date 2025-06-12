from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

import core.constants as cnsts
from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Recipe, ShoppingCart, Tag)

admin.site.unregister(Group)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1
    validate_min = True
    autocomplete_fields = ('ingredient',)


class CookingTimeFilter(SimpleListFilter):
    title = _('Время приготовления')
    parameter_name = 'cooking_time_group'

    def lookups(self, request, model_admin):
        return (
            ('short', _('до 30 минут')),
            ('medium', _('от 30 до 60 минут')),
            ('long', _('более 60 минут')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(
                cooking_time__lt=cnsts.SHORT_COOKING_TIME
            )
        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=cnsts.SHORT_COOKING_TIME,
                cooking_time__lte=cnsts.LONG_COOKING_TIME
            )
        if self.value() == 'long':
            return queryset.filter(
                cooking_time__gt=cnsts.LONG_COOKING_TIME
            )
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'pub_date',
        'display_tags', 'display_ingredients',
        'favorite_count', 'image_preview',
    )
    list_display_links = ('name',)
    readonly_fields = ('image_preview', 'favorite_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', CookingTimeFilter)
    inlines = (IngredientInRecipeInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return (
            queryset
            .select_related('author')
            .prefetch_related('tags', 'ingredients')
            .annotate(favorite_count=Count('in_favorites'))
            .order_by('-pub_date')
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        return ', '.join(i.name for i in obj.ingredients.all())

    @admin.display(description='Превью изображения')
    def image_preview(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" width="180" height="160">'
        )

    @admin.display(description='В избранном (раз)')
    def favorite_count(self, obj):
        return obj.favorite_count


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    @admin.display(description='Пользователь')
    def user_username(self, obj):
        return obj.user.username


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    @admin.display(description='Пользователь')
    def user_username(self, obj):
        return obj.user.username
