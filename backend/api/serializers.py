from django.db import transaction
from django.urls import reverse
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .validators import validate_ingredients, validate_tags
from core.serializers import (
    BaseFavoriteShoppingCartSerializer,
    ShortRecipeSerializer
)
from core.short_links import encode_id
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Follow, User


class UserSerializer(DjoserUserSerializer):
    """Сериализует данные пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar',
        )

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and obj is not None
            and obj.subscribers.filter(user=request.user).exists()
        )


class UserAvatarUploadSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class FollowCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            ),
        )

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        recipes_limit = self.context.get('recipes_limit')
        return FollowReadSerializer(
            instance.author,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            }
        ).data


class FollowReadSerializer(UserSerializer):
    """Сериализатор подписок с краткой информацией о рецептах."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()

        try:
            recipes = recipes[:int(self.context.get('recipes_limit'))]
        except (TypeError, ValueError):
            pass

        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'name', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        fields = '__all__'
        read_only_fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте (только для чтения)."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте (только для записи)."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Количество ингредиента должно быть больше 0.'
        }
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецепта."""

    ingredients = IngredientInRecipeWriteSerializer(many=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        validate_ingredients(data.get('ingredients'))
        validate_tags(data.get('tags'))
        
        if data.get('image') in [None, '']:
            raise serializers.ValidationError(
                {'image': 'Это поле обязательно.'}
            )
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='ingredientinrecipe_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_shoppingcarts.filter(user=request.user).exists()


class ShortRecipeLinkSerializer(serializers.Serializer):
    """Сериализатор просмотра краткой ссылки на рецепт."""

    short_link = serializers.SerializerMethodField()

    def get_short_link(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        url = reverse('recipe-shortlink-redirect', args=[encode_id(obj.id)])
        return request.build_absolute_uri(url)

    def to_representation(self, instance):
        return {
            'short-link': self.get_short_link(instance)
        }


class FavoriteSerializer(BaseFavoriteShoppingCartSerializer):
    """Сериализатор избранного."""

    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(BaseFavoriteShoppingCartSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
