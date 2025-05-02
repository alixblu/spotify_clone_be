from djongo import models
from bson import ObjectId

from spotify_app.models import Playlist, Song, Artist, Album
from user_management.models import User

class PlaylistSong(models.Model):
    # Không cần thêm đuôi _id vào tên trường vì Django sẽ tự động thêm
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'song') # Đảm bảo không có bài hát nào được thêm nhiều lần vào cùng một playlist
        db_table = "playlist_songs"


class ArtistPerform(models.Model):
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('artist_id', 'song_id')
        db_table = "artist_performances"

    def __str__(self):
        return f"Artist {self.artist_id} performed Song {self.song_id}"

class FavoriteSong(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'song_id')
        db_table = "favorite_songs"

    def __str__(self):
        return f"User {self.user_id} favorited Song {self.song_id}"
    
class FavoriteAlbum(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'album_id')
        db_table = "favorite_albums"

    def __str__(self):
        return f"User {self.user_id} favorited Album {self.album_id}"
    
class FavoritePlaylist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_id = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'playlist_id')
        db_table = "favorite_playlists"

    def __str__(self):
        return f"User {self.user_id} favorited Playlist {self.playlist_id}"


# class PlaylistSongHistory(models.Model):
#     playlist_id = models.ForeignKey(Playlist, on_delete=models.CASCADE)
#     song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)
#     removed_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         unique_together = ('playlist_id', 'song_id')
#         ordering = ['-added_at']