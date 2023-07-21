from rest_framework import serializers

from users.serializers import CustomUserSerializer
from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeIngredient,
                            Favorite, Shopping_cart)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('__all__')


class RecipeSerSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta():
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, fav_recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Shopping_cart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    pass


class FavoriteSerializer(serializers.ModelSerializer):
    pass


class ShoppingSerializer(serializers.ModelSerializer):
    pass


class RecipeShortDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
