from django.urls import include, path


app_name = 'api'

urlpatterns = [
    path('', include('users.urls', namespace='users')),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
