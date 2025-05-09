from django.urls import path
from . import songviews
from . import albumviews
from . import playlistviews
from . import playlist_songviews
urlpatterns = [

    path('songs/', songviews.list_songs, name='list_songs'),
    path('songs/upload/', songviews.upload_song, name='upload_song'),
    path('songs/<str:song_id>/', songviews.get_song, name='get_song'),
    path('songs/<str:song_id>/update/', songviews.update_song, name='update_song'),
    path('songs/<str:song_id>/delete/', songviews.delete_song, name='delete_song'),
    path('songs/<str:song_id>/hide/', songviews.hide_song, name='hide_song'),
    path('songs/<str:song_id>/unhide/', songviews.unhide_song, name='unhide_song'),
    path('albums/', albumviews.list_albums, name='list_albums'),
    path('albums/upload/', albumviews.create_album, name='upload_album'),
    path('albums/<str:album_id>/', albumviews.get_album, name='get_album'),
    path('albums/<str:album_id>/update/', albumviews.update_album, name='update_album'),
    path('albums/<str:album_id>/delete/', albumviews.delete_album, name='delete_album'),
    # PLAYLIST
    path('playlists/create', playlistviews.create_playlist, name='create_playlist'),
    path('playlists/<str:playlist_id>', playlistviews.get_playlist_by_id, name='get_playlist_by_id'),
    path('playlists/<str:playlist_id>/update', playlistviews.update_playlist, name='update_playlist'),
    path('playlists/<str:playlist_id>/delete', playlistviews.delete_playlist, name='delete_playlist'),
    # PLAYLIST SONGS
    path('playlists/<str:playlist_id>/add_songs', playlist_songviews.add_songs_to_playlist, name='add_songs_to_playlist'),
]


