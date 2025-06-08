from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

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


class IngredientInRecipeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_ingredient = any(
            not form.cleaned_data.get('DELETE', False)
            for form in self.forms
            if form.cleaned_data.get('ingredient')
        )
        if not has_ingredient:
            raise ValidationError('Добавьте хотя бы один ингредиент.')


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    formset = IngredientInRecipeInlineFormSet
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time',
        'favorite_count', 'image_preview'
    )
    list_display_links = ('name',)
    readonly_fields = ('image_preview', 'favorite_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="180" height="160">'
            )
        return 'Изображение отсутствует'
    image_preview.short_description = 'Прросмотр изображения'

    def favorite_count(self, obj):
        return obj.in_favorites.count()
    favorite_count.short_description = 'В избранном (раз)'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'recipe')
    search_fields = ('user__username', 'recipe__name')

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'
