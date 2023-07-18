from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Tag, TagsAdmin)
