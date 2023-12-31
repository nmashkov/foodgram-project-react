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
from api.filters import RecipeFilter, IngredientFilter
from api.utils import data_generation
from users import permissions as users_permissions
from users.serializers import RecipeShortDetailSerializer


'''
Для ревьювера:
Максим, добрый день!
Понимаю, что нельзя общаться с ревьювером, но текущая ситуация меня вынуждает
выйти с Вами на связь.
Хочу сказать, что и вправду можно зайти на страницу редактирования рецепта,
введя в адресную строку '/edit', но если текущий пользователь не автор и не
админ, то при сохранении рецепта он получит ошибку
'You do not have permission to perform this action.', а при нажатии кнопки
удаления и вовсе ничего не произойдёт, при этом, если изменить чужой рецепт
с правами админа, то редактирование и удаление возможно, т.е. проверка прав
работает, как и требуется заданием. Почему фронтенд позволяет зайти на страницу
редактирования рецепта - я не знаю, если делать такие проверки или через
постман, то всё работает.
Так же заметил проблему с отображением страницы пользователя. Фронт никак
не хочет пускать анонима на страницу другого пользователя, хотя через тот же
постман запрос проходит. Как бы я не менял доступ через права и не переписывал
код, эта проблема сохраняется.
Если можно, то мой тг для связи @alQadmus
'''


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Функция представления для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Функция представления для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Функция представления для рецептов."""
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = (users_permissions.IsAuthorAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCPDSerializer

    @action(methods=('post', 'delete'),
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавление/удаление из избранного."""
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    @action(methods=('post', 'delete'),
            detail=True,
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
        """Функция создания и выгрузки пользователю его список покупок."""
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
