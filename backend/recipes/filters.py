from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from recipes.models import Tag


User = get_user_model()


class IngredientFilter(SearchFilter):
    """Определение фильтра для ингредиента"""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Фильтрация для списка рецептов."""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',)
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        """Функция проверки рецепта в избранном."""
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(
                favoriters__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Функция проверки рецепта в списке покупок."""
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(
                shoppers__user=self.request.user
            )
        return queryset
