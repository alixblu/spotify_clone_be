from django.urls import path
from .views import fetch_new_releases
from .views import search_edm_artists

urlpatterns = [
    path('new-releases/', fetch_new_releases, name='fetch_new_releases'),
    path('top-artists/', search_edm_artists, name='search_edm_artists'),
]