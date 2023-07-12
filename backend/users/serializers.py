from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(regex=r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$',
                                      max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя.')
        return username


class UserRecieveTokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        read_only_fields = ('username', 'confirmation_code',)

    def validate_username(self, username):
        if len(username) > 150:
            raise serializers.ValidationError(
                'Имя пользователя должно быть меньше 151 символа.')
        return username


class UsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(regex=r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$',
                                      max_length=150)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email'],
                message='Имя пользователя и почта должны быть уникальными.'
            )
        ]
