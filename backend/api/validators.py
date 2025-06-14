from rest_framework import serializers


def validate_ingredients(ingredients):
    if not ingredients:
        raise serializers.ValidationError('Добавьте хотя бы один ингредиент.')

    ingredient_ids = [item.get('id') for item in ingredients]
    if len(ingredient_ids) != len(set(ingredient_ids)):
        raise serializers.ValidationError('Ингредиенты не должны повторяться.')

    return ingredients


def validate_tags(tags):
    if not tags:
        raise serializers.ValidationError('Добавьте хотя бы один тег.')

    if len(tags) != len(set(tags)):
        raise serializers.ValidationError('Теги не должны повторяться.')

    return tags
