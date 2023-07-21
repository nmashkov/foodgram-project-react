from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator


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
        return self.name


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
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Теги',
                                  blank=False)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор',
                               blank=False)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         through_fields=("recipe",
                                                         "ingredient"),
                                         verbose_name='Список ингредиентов')
    name = models.CharField(verbose_name='Название',
                            max_length=200, blank=False)
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/images/',
                              null=False, blank=False)
    text = models.TextField(verbose_name='Описание', blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],
        blank=False)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(blank=False,
                                         verbose_name='Количество',
                                         validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    fav_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriters',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'fav_recipe'],
                name='unique_user_fav_recipe'
            )
        ]


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppers',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
