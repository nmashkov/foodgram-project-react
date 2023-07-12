from django.contrib import admin

from users.models import User


class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


admin.site.register(User, UsersAdmin)
