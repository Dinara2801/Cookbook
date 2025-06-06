import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Recipe


class Base64ImageField(serializers.ImageField):
    """Сериализатор для кодирования ссылки на изображение."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор рецепта для возврата при добавлении."""

    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для избранного и списка покупок."""

    def validate(self, data):
        if self.Meta.model.objects.filter(
            user=self.context['request'].user,
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен.'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data
