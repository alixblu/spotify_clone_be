from django.urls import path
from . import views

urlpatterns = [
    path('artistperform/upload/<str:artist_id>/', views.add_artist_performance, name='add_artist_performance'),
]