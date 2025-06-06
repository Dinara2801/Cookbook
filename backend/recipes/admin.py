from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import Favorite, Ingredient, IngredientInRecipe, Recipe, Tag

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
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
