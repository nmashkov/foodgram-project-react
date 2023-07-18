from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import TagViewSet


app_name = 'recipes'

router_recipes = DefaultRouter()
router_recipes.register(
    'tags',
    TagViewSet,
    basename='tags'
)

urlpatterns = [
    path('', include(router_recipes.urls)),
]
