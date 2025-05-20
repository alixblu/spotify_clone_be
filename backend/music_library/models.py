from djongo import models
from bson import ObjectId
from django.utils import timezone

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
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    # Sửa lại không gắn _id sau artist và song vì mongodb tự động thêm
    class Meta:
        unique_together = ('artist', 'song')
        db_table = "artist_performances"

    def __str__(self):
        return f"Artist {self.artist} performed Song {self.song}"
    
class FavoriteSong(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'song') 
        db_table = "favorite_songs"

    # def __str__(self):
    #     return f"User {self.user} favorited Song {self.song}"
    
class FavoriteAlbum(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)  # Thay auto_now_add bằng default

    class Meta:
        unique_together = ('user', 'album')
        db_table = "favorite_albums"

    # def __str__(self):
    #     return f"User {self.user_id} favorited Album {self.album_id}"
    
class FavoritePlaylist(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)  # Thay auto_now_add bằng default

    class Meta:
        unique_together = ('user', 'playlist')
        db_table = "favorite_playlists"

    def __str__(self):
        return f"User {self.user} favorited Playlist {self.playlist}"


# class PlaylistSongHistory(models.Model):
#     playlist_id = models.ForeignKey(Playlist, on_delete=models.CASCADE)
#     song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)
#     removed_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         unique_together = ('playlist_id', 'song_id')
#         ordering = ['-added_at']