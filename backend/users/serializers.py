from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(max_length=254, allow_blank=False,
                                   required=True)
    first_name = serializers.CharField(max_length=150, allow_blank=False,
                                       required=True)
    last_name = serializers.CharField(max_length=150, allow_blank=False,
                                      required=True)

    class Meta():
        model = User
        fields = ('email', 'id',
                  'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return False
