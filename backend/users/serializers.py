from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import Subscription
from recipes.models import Recipe


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания нового пользователя."""
    email = serializers.EmailField(max_length=254, allow_blank=False,
                                   required=True)
    first_name = serializers.CharField(max_length=150, allow_blank=False,
                                       required=True)
    last_name = serializers.CharField(max_length=150, allow_blank=False,
                                      required=True)

    class Meta():
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя.')
        return username


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.subscribers.filter(user=request.user).exists()
        else:
            return False


class RecipeShortDetailSerializer(serializers.ModelSerializer):
    """Сериализатор краткого описания рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления подписки на автора."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('user',)
        extra_kwargs = {'author': {'write_only': True}}


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор представления всех подписок пользователя."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortDetailSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return obj.subscribers.filter(user=request.user).exists()
