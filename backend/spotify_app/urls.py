from django.urls import path
from . import songviews
from . import albumviews
from . import playlistviews
from . import playlist_songviews
from . import artistviews
from . import followviews
urlpatterns = [
    # SONG
    path('songs/', songviews.list_songs, name='list_songs'),
    path('songs/upload/', songviews.upload_song, name='upload_song'),
    path('songs/<str:song_id>/', songviews.get_song, name='get_song'),
    path('songs/<str:song_id>/update/', songviews.update_song, name='update_song'),
    path('songs/<str:song_id>/delete/', songviews.delete_song, name='delete_song'),
    path('songs/<str:song_id>/hide/', songviews.hide_song, name='hide_song'),
    path('songs/<str:song_id>/unhide/', songviews.unhide_song, name='unhide_song'),
    path('albums/<str:album_id>/songs/<str:song_id>/delete', songviews.delete_song_inAlbum, name='delete_song'),
    path('songs/get_songs_by_album/<str:album_id>', songviews.get_songs_by_album, name='get_songs_by_album'),
    # ALBUM
    path('albums/', albumviews.list_albums, name='list_albums'),
    path('albums/create/', albumviews.create_album, name='create_album'),
    path('albums/<str:album_id>/', albumviews.get_album, name='get_album'),
    path('albums/<str:album_id>/update/', albumviews.update_album, name='update_album'),
    path('albums/<str:album_id>/delete/', albumviews.delete_album, name='delete_album'),
    # PLAYLIST
    path('playlists/getalls/<str:user_id>/', playlistviews.get_alls_playlists_by_user, name='get_all_playlists'),
    path('playlists/create', playlistviews.create_playlist, name='create_playlist'),
    path('playlists/<str:playlist_id>', playlistviews.get_playlist_by_id, name='get_playlist_by_id'),
    path('playlists/<str:playlist_id>/update', playlistviews.update_playlist, name='update_playlist'),
    path('playlists/<str:playlist_id>/delete', playlistviews.delete_playlist, name='delete_playlist'),
    # PLAYLIST SONGS
    path('playlists/<str:playlist_id>/add_songs', playlist_songviews.add_songs_to_playlist, name='add_songs_to_playlist'),
    # path('playlists/<str:playlist_id>/remove_songs', playlist_songviews.remove_songs_from_playlist, name='remove_songs_from_playlist'),
    path('playlists/<str:playlist_id>/songs', playlist_songviews.get_songs_in_playlist, name='get_songs_in_playlist'),
    # ARTIST
    path('artists/', artistviews.get_all_artists, name='get_all_artists'),
    path('artists/create', artistviews.create_artist, name='create_artist'),
    path('artists/<str:artist_id>', artistviews.get_artist_by_id, name='get_artist_by_id'),
    path('artists/<str:artist_id>/update', artistviews.update_artist, name='update_artist'),
    path('artists/<str:artist_id>/delete', artistviews.delete_artist, name='delete_artist'),
    path('artists/<str:artist_id>/hide', artistviews.hide_artist, name='hide_artist'),
    path('artists/<str:artist_id>/unhide', artistviews.unhide_artist, name='unhide_artist'),
    path('artists/<str:artist_id>/albums', artistviews.get_artist_albums, name='get_albums_by_artist'),
    # FOLLOW
    # Lấy danh sách các nghệ sĩ mà user đã follow
    path('follow/<str:user_id>/artists/', followviews.get_followed_artists, name='get_followed_artists'),
    # Lấy danh sách các user mà user đã follow
    path('follow/<str:user_id>/users/', followviews.get_followed_users, name='get_followed_users'),
    # Người dùng follow target (nghệ sĩ hoặc user khác)
    path('follow/', followviews.follow_target, name='follow_target'),
    # path('follow/<str:user_id>/<str:followed_id>/unfollow/', playlistviews.unfollow_user, name='unfollow_user'),
]


