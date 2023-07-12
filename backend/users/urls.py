from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (APIUserSignup, CustomTokenViewBase, UsersViewSet)


app_name = 'users'

router_users = DefaultRouter()
router_users.register(
    'users',
    UsersViewSet,
    basename='users')

urlpatterns = [
    path('auth/signup/', APIUserSignup.as_view()),
    path('auth/token/', CustomTokenViewBase.as_view()),
    path('', include(router_users.urls)),
]
