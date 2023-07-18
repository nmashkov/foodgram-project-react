from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import TagViewSet, IngredientViewSet


app_name = 'recipes'

router_recipes = DefaultRouter()
router_recipes.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router_recipes.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router_recipes.urls)),
]
