from django.urls import path
from . import views

urlpatterns = [
    # ARTIST PERFORMANCE
    path('artistperform/upload/<str:artist_id>/', views.add_artist_performance, name='add_artist_performance'),
    path('artistperform/<str:artist_id>/', views.get_artist_performances, name='get_artist_performance'),
    path('artistperform/song/<str:song_id>/', views.get_song_artists_performances, name='get_artist_performance_by_song'),
    path('artistperform/<str:artist_id>/<str:song_id>/delete/', views.delete_artist_performance, name='delete_artist_performance'),
    # FAVORITE SONG
    path('favorite_songs/<str:user_id>/', views.get_favorite_songs, name='get_favorite_songs'),
    path('favorite_songs/<str:user_id>/create', views.create_favorite_songs, name='add_favorite_song'),
    path('favorite_songs/<str:user_id>/<str:song_id>/delete/', views.delete_favorite_song, name='delete_favorite_song'),
    path('favorite_songs/<str:user_id>/favorite/songs/summary/', views.get_favorite_songs_summary, name='check_favorite_song'),
    # FAVORITE ALBUM
    path('favorite_albums/<str:user_id>/', views.get_favorite_albums, name='get_favorite_albums'),
    path('favorite_albums/<str:user_id>/create', views.create_favorite_album, name='add_favorite_album'),
    path('favorite_albums/<str:user_id>/<str:album_id>/delete/', views.delete_favorite_album, name='delete_favorite_album'),
    # FAVORITE PLAYLIST
    path('favorite_playlists/<str:user_id>/', views.get_favorite_playlists, name='get_favorite_playlists'),
    path('favorite_playlists/<str:user_id>/create', views.create_favorite_playlist, name='add_favorite_playlist'),
    path('favorite_playlists/<str:user_id>/<str:playlist_id>/delete/', views.delete_favorite_playlist, name='delete_favorite_playlist'),
]