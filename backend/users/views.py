from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, permissions, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import AccessToken

from users.permissions import IsAdmin
from users.serializers import (
    UserSignupSerializer, UserRecieveTokenSerializer,
    UsersSerializer
)


User = get_user_model()


class APIUserSignup(APIView):
    """
    Регистрация нового пользователя и повторная отправка кода подтверждения.
    Права доступа: Доступно без токена.
    """
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.filter(username=username, email=email).first()
            token = default_token_generator.make_token(user)
        elif User.objects.filter(username=username).exists():
            user = User.objects.filter(username=username).first()
            if str(user.email) != email:
                return Response('Пользователь с таким именем уже существует.',
                                status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email).first()
            if str(user.username) != username:
                return Response('Пользователь с такой почтой уже существует.',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            user = get_object_or_404(User, username=username)
            token = default_token_generator.make_token(user)
        send_mail(
            f'Confirmation code for {user.role} {username}',
            f'Confirmation code for {user.role} {username}: '
            f'{token}',
            settings.DEFAULT_FROM_EMAIL,
            [f'{email}']
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenViewBase(TokenViewBase):
    """
    Получение JWT-токена.
    Права доступа: Доступно без токена.
    """
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username or not confirmation_code:
            return Response('Необходимы username и код подтверждения.',
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            user = User.objects.filter(username=username).first()
        else:
            return Response('Пользователь не найден.',
                            status=status.HTTP_404_NOT_FOUND)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Неверный код подтверждения.',
                            status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response({"token": f'{token}'}, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """
    Функция представления и регистрации пользователей администратором
    (Права доступа: Администратор),
    А также получения и изменения данных своей учётной записи
    (Права доступа: Любой авторизованный пользователь).
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username).exists():
            user = User.objects.filter(username=username).first()
            if str(user.email) != email:
                return Response('Пользователь с таким именем уже существует.',
                                status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email).first()
            if str(user.username) != username:
                return Response('Пользователь с такой почтой уже существует.',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=UsersSerializer,
            url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = get_object_or_404(User, username=request.user)
        role = user.role
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=role)
        return Response(serializer.data, status=status.HTTP_200_OK)
