from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (AvatarView, DownloadShoppingCartView, FavoriteView,
                    FollowListView, FollowView, IngredientViewSet,
                    RecipeViewSet, ShoppingCartView, ShortLinkRedirectView,
                    ShortRecipeLinkView, TagViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'users',
    UserViewSet,
    basename='users'
)

users_urlpatterns = [
    path(
        'me/avatar/',
        AvatarView.as_view(),
        name='avatar'
    ),
    path(
        'subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        '<int:user_id>/subscribe/',
        FollowView.as_view(),
        name='subscribe'
    ),
]

recipes_id_urlpatterns = [
    path(
        'shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart'
    ),
    path(
        'favorite/',
        FavoriteView.as_view(),
        name='favorite'
    ),
    path(
        'get-link/',
        ShortRecipeLinkView.as_view(),
        name='short-recipe-link'
    ),
]

recipes_urlpatterns = [
    path(
        'download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download-shopping-list'
    ),
    path(
        '<int:recipe_id>/',
        include(recipes_id_urlpatterns)
    ),
]

urlpatterns = [
    path('users/', include(users_urlpatterns)),
    path('recipes/', include(recipes_urlpatterns)),
    path('r/<str:encoded>/', ShortLinkRedirectView.as_view(),
         name='recipe-shortlink-redirect'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
