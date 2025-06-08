from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowReadSerializer, IngredientSerializer, 
                          PasswordChangeSerializer, RecipeWriteSerializer,
                          ShortRecipeLinkSerializer, TagSerializer,
                          UserAvatarUploadSerializer,
                          UserRegistrationSerializer, UserSerializer)
from core.serializers import ShortRecipeSerializer
from core.short_links import decode_id
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from users.models import Follow, User


def add_remove_recipe(request, recipe_id, model, add_error_msg=''):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user

    if request.method == 'POST':
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': add_error_msg}, status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(ShortRecipeSerializer(
            recipe, context={'request': request}
        ).data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для получения списока пользователей или создания нового."""

    http_method_names = ('get', 'post')
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return UserSerializer
        return UserRegistrationSerializer

    @action(methods=('get',), detail=False, url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me_info_get(self, request):
        """Метод для получения информации о текущем пользователе."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('post',), detail=False, url_path='set_password',
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        """Метод для изменения пароля."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Пароль успешно изменён.'},
                        status=status.HTTP_204_NO_CONTENT)


class AvatarView(views.APIView):
    """Представление для загрузки и удаления аватара пользователя."""

    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        if 'avatar' not in request.data:
            return Response(
                {'avatar': 'Это поле обязательно для загрузки аватара.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        serializer = UserAvatarUploadSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowView(views.APIView):
    """Представление для подписки и отписки от пользователей."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        user = request.user

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Follow.objects.filter(user=user, following=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Follow.objects.create(user=user, following=author)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                recipes_limit = None
        serializer = FollowReadSerializer(
            author, context={
                'request': request, 'recipes_limit': recipes_limit
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        obj = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, id=user_id)
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowListView(generics.ListAPIView):
    """Представление для отображения списка подписок пользователя."""

    serializer_class = FollowReadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            context['recipes_limit'] = int(recipes_limit)
        else:
            context['recipes_limit'] = None
        return context


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для чтения информации о тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для чтения информации об ингредиентах."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для создания, редактирования и чтения рецептов."""

    serializer_class = RecipeWriteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=user, recipe=OuterRef('pk')
                )),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user=user, recipe=OuterRef('pk')
                ))
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )

        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (IsAuthorOrReadOnly(),)


class ShortRecipeLinkView(views.APIView):
    """Представление для получения короткой ссылки на рецепт."""

    def get(self, request, recipe_id):
        return Response(ShortRecipeLinkSerializer(
            get_object_or_404(Recipe, id=recipe_id),
            context={'request': request}
        ).data)


class ShortLinkRedirectView(View):
    """Представление для перенаправления по короткой ссылке на рецепт."""

    def get(self, request, encoded):
        recipe_id = decode_id(encoded)
        if recipe_id is None:
            raise Http404('Неверная ссылка')

        get_object_or_404(Recipe, id=recipe_id)
        return redirect(f'/recipes/{recipe_id}/')


class FavoriteView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        return add_remove_recipe(
            request,
            recipe_id,
            Favorite,
            'Вы уже добавили рецепт в избранное.'
        )

    def delete(self, request, recipe_id):
        return add_remove_recipe(
            request,
            recipe_id,
            Favorite
        )


class ShoppingCartView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_id):
        return add_remove_recipe(
            request,
            recipe_id,
            ShoppingCart,
            'Вы уже добавили рецепт в список покупок.'
        )

    def delete(self, request, recipe_id):
        return add_remove_recipe(
            request,
            recipe_id,
            ShoppingCart
        )


class DownloadShoppingCartView(views.APIView):
    """Представление для скачивания списка покупок в виде текстового файла."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in_shoppingcarts__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        lines = ['Список покупок:\n']

        for item in ingredients:
            lines.append(
                f'{item["ingredient__name"]} - {item["total_amount"]} '
                f'{item["ingredient__measurement_unit"]}\n'
            )

        text_content = ''.join(lines)
        response = HttpResponse(
            text_content,
            content_type='text/plain; charset=utf-8'
        )
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        return response
