from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=200,
        blank=False
    )
    color = models.CharField(max_length=7, blank=False)
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        db_index=True,
        max_length=200,
        blank=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=200,
        blank=False
    )
    measurement_unit = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through='Tags', blank=False,
                                  verbose_name='Теги')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               blank=False,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='Ingredients',
                                         verbose_name='Список ингредиентов')
    name = models.CharField(verbose_name='Картинка',
                            max_length=200, blank=False)
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/images/',
                              null=False, blank=False)
    text = models.TextField(verbose_name='Описание', blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)', blank=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_user_subscribing'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriter'
    )
    favoriting = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriting'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favoriting'],
                name='unique_user_favoriting'
            )
        ]


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopper'
    )
    shopping = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'shopping'],
                name='unique_user_shopping'
            )
        ]
