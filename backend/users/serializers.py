from django.contrib.auth import get_user_model
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email=serializers.EmailField(max_length=254, allow_blank=False, required=True)
    first_name=serializers.CharField(max_length=150, allow_blank=False, required=True)
    last_name=serializers.CharField(max_length=150, allow_blank=False, required=True)

    class Meta():
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
