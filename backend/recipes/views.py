from rest_framework import viewsets
from rest_framework.decorators import action

from recipes.models import Tag, Ingredient, Recipe
from recipes.serializers import (TagSerializer, IngredientSerializer,
                                 RecipeSerSerializer, RecipeCreateSerializer,
                                 FavoriteSerializer, ShoppingSerializer)
from users import permissions


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Функция представления для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Функция представления для ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Функция представления для рецептов.'''
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthorAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action == 'shopping_cart':
            return ShoppingSerializer
        if self.action == 'download_shopping_cart':
            return ShoppingSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete'), detail=True)
    def favorite(self, request, id):
        pass

    @action(methods=('post', 'delete'), detail=True)
    def shopping_cart(self, request, id):
        pass

    @action(methods=('get'), detail=True)
    def download_shopping_cart(self, request):
        pass
