from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.serializers import (CustomUserSerializer, SubscriptionsSerializer,
                               SubscribeSerializer)
from users.models import Subscription


User = get_user_model()


class UserViews(UserViewSet):
    """
    Функция работы с пользователем: профиль, подписка на автора,
    список подписок.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Функция отображения самого пользователя."""
        user = self.request.user
        serializer = CustomUserSerializer(
            user,
            context={
                'request': request
            }
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id):
        """"Функция создания и удаления подписки."""
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            user,
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            if author == user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.')
            if author.subscribers.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Уже подписаны.')
            Subscription.objects.create(user=user, author=author)
            serializer.save()
            return Response({'Message': 'Subscribed'},
                            status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            subscription = get_object_or_404(Subscription,
                                             user=user, author=author)
            subscription.delete()
            return Response({'Message': 'Unsubscribed'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Функция подписок пользователя."""
        user = request.user
        queryset = User.objects.filter(subscriptions__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
