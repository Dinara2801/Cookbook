import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers


class UsernameValidator(UnicodeUsernameValidator):
    """Валидация имени пользователя."""

    def __call__(self, value):
        super().__call__(value)

        if value.lower() == 'me':
            raise ValidationError('Имя пользователя "me" запрещено.')

        regex = r'^[\w.@+-]+$'
        if not re.match(regex, value):
            raise ValidationError(
                'Имя пользователя может содержать только '
                'буквы, цифры и символы @/./+/-/_'
            )
        return value


def validate_ingredients(ingredients):
    if not ingredients:
        raise serializers.ValidationError('Добавьте хотя бы один ингредиент.')

    seen = set()
    for item in ingredients:
        ingredient = item.get('ingredient')
        if ingredient in seen:
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        seen.add(ingredient)

    return ingredients


def validate_tags(tags):
    if not tags:
        raise serializers.ValidationError('Добавьте хотя бы один тег.')

    if len(tags) != len(set(tags)):
        raise serializers.ValidationError('Теги не должны повторяться.')

    return tags
