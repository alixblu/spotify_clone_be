from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='custom_login'),
    path('register/', views.custom_register, name='custom_register'),
    path('songs/', views.list_songs, name='list_songs'),
    path('songs/upload/', views.create_song, name='create_song'),
    path('songs/<str:song_id>/', views.get_song, name='get_song'),
    path('songs/<str:song_id>/update/', views.update_song, name='update_song'),
    path('songs/<str:song_id>/delete/', views.delete_song, name='delete_song'),
]


