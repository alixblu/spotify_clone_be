from django.urls import path
from . import views
from . import albumviews
urlpatterns = [

    path('songs/', views.list_songs, name='list_songs'),
    path('songs/upload/', views.upload_song, name='upload_song'),
    path('songs/<str:song_id>/', views.get_song, name='get_song'),
    path('songs/<str:song_id>/update/', views.update_song, name='update_song'),
    path('songs/<str:song_id>/delete/', views.delete_song, name='delete_song'),
    path('albums/', albumviews.list_albums, name='list_albums'),
    path('albums/upload/', albumviews.create_album, name='upload_album'),
    path('albums/<str:album_id>/', albumviews.get_album, name='get_album'),
    path('albums/<str:album_id>/update/', albumviews.update_album, name='update_album'),
    path('albums/<str:album_id>/delete/', albumviews.delete_album, name='delete_album'),
]


