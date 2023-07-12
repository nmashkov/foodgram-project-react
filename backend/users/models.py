from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    username = models.TextField(
        'Имя пользователя'
    )
    first_name = models.TextField(
        'Имя'
    )
    last_name = models.TextField(
        'Фамилия'
    )

    REQUIRED_FIELDS = ['email', 'username', 'first_name', 'last_name']
