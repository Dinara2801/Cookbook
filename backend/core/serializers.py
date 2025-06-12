from rest_framework import serializers

from recipes.models import Recipe


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
                f'Рецепт уже добавлен в {self.Meta.model._meta.verbose_name}.'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data
