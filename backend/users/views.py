from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, serializers, mixins, permissions

from users.serializers import SubscribeSerializer, SubscriptionsSerializer


User = get_user_model()


class SubscribeViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    '''Функция создания и удаления подписки.'''
    serializer_class = SubscribeSerializer
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        subscriptions = user.subscriptions.all()
        return subscriptions

    def perform_create(self, serializer):
        if serializer.validated_data['author'] == self.request.user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        serializer.save(user=self.request.user)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    '''Функция представления подписок.'''
    serializer_class = SubscriptionsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        subscriptions = user.subscriptions.all()
        return subscriptions
