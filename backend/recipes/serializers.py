import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeIngredient,
                            Favorite, ShoppingCart)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_measurement_unit(self, ingredient):
        return ingredient.ingredient.measurement_unit

    def get_name(self, ingredient):
        return ingredient.ingredient.name


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True,
        source='recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_ShoppingCart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)

    class Meta():
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_ShoppingCart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_ShoppingCart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCPDSerializer(serializers.ModelSerializer):
    """Recipe Create-Patch-Delete Serializer."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True,
    )
    ingredients = IngredientInRecipeWriteSerializer(many=True, required=True)
    image = Base64ImageField(required=True)

    class Meta():
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image', 'name',
                  'text', 'cooking_time')

    def create_ingredients_amounts(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in value:
            ingredient = Ingredient.objects.get(id=item['id'])
            if ingredient in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингридиенты не должны повторяться!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError({
                'tags': 'Веберите как минимум один тег!'
            })
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise serializers.ValidationError({
                'tags': 'Теги должны быть уникальными!'
            })
        return value
