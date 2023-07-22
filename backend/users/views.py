from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.serializers import SubscribeSerializer, SubscriptionsSerializer
from users.models import Subscription


User = get_user_model()


class SubscribeViewSet(UserViewSet):
    """Функция создания и удаления подписки."""

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscribeSerializer(
            user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            if author == user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.')
            if Subscription.objects.filter(user=user, author=author).exists():
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


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Функция представления подписок."""
    serializer_class = SubscriptionsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        return subscriptions
