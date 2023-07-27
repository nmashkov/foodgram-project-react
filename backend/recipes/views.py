from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            Favorite, ShoppingCart)
from recipes.serializers import (TagSerializer, IngredientSerializer,
                                 RecipeSerializer, RecipeCPDSerializer)
from recipes.filters import RecipeFilter, IngredientFilter
from users import permissions as users_permissions
from users.serializers import RecipeShortDetailSerializer


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
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Функция представления для рецептов.'''
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = (users_permissions.IsAuthorAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def _create_or_delete_item(request, recipe, model, serializer):
        try:
            item = model.objects.get(user=request.user, recipe=recipe)
            if request.method == 'DELETE':
                item.delete()
                return Response({'Message': 'Deleted'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except model.DoesNotExist:
            if request.method == 'POST':
                item = model.objects.create(user=request.user, recipe=recipe)
                serializer = serializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCPDSerializer

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление/удаление из избранного."""
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавление/удаление из списка покупок."""
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        """Функция добавления."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortDetailSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        """Функция удаления."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppers__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        if not user.shopping.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return data_generation(user, ingredients)


def data_generation(user, ingredients):
    today = datetime.today()
    shopping_list = (
        f'Список покупок для: {user.get_full_name()}\n\n'
        f'Дата: {today:%Y-%m-%d}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    shopping_list += f'\n\nFoodgram ({today:%Y})'
    filename = f'{user.username}_shopping_list'
    response = HttpResponse(
        shopping_list, content_type='text/plain,charset=utf8'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
