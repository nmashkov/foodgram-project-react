from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'pub_date')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
