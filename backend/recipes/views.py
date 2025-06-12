from django.http import HttpResponsePermanentRedirect
from django.views import View

from recipes.models import Recipe
from core.short_links import decode_id


class ShortLinkRedirectView(View):
    """Представление для перенаправления по короткой ссылке на рецепт."""

    def get(self, request, encoded):
        recipe_id = decode_id(encoded)
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            target_url = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        except (Recipe.DoesNotExist, TypeError):
            target_url = request.build_absolute_uri('/not_found')

        return HttpResponsePermanentRedirect(target_url)
