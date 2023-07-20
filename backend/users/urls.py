from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import SubscriptionsViewSet, SubscribeViewSet


app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(
    r'users/(?P<id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'})),
    # path('users/<int:pk>/subscribe/',
    #     SubscribeViewSet.as_view({'post': 'create',
    #                               'delete': 'destroy'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
