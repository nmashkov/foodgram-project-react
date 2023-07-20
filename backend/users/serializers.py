from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import Subscription
from recipes.models import Recipe


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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),)

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
                message='Нельзя подписаться дважды на одного и того же автора.'
            )
        ]


class RecipeShortDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    recipes = RecipeShortDetailSerializer(
        many=True, source='author.recipes', read_only=True
    )
    recipes_count = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_recipes_count(obj):
        return obj.author.recipes.count()

    class Meta:
        model = Subscription
        fields = ('id', 'author', 'recipes', 'recipes_count')
