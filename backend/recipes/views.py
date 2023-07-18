from rest_framework import viewsets

from recipes.models import Tag
from recipes.serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Функция представления для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
