from django.urls import path
from .views import fetch_new_releases

urlpatterns = [
    path('new-releases/', fetch_new_releases, name='fetch_new_releases'),
]