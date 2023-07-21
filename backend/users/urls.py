from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import SubscriptionsViewSet, SubscribeViewSet


app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(
    r'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions'
)
router_v1.register(r'users', SubscribeViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
