from djongo import models

# Create your models here.
from djongo import models

# covert str to ObjectId when get data from DB and vice versa
class ArtistPerform(models.Model):
    artist_id = models.CharField(max_length=255, null=False)
    song_id = models.CharField(max_length=255, null=False)

    def __str__(self):
        return f"Artist{self.artist_id} Performs {self.song_id}"
    

class FavoriteSong(models.Model):
    user_id = models.CharField(max_length=255, null=False)
    song_id = models.CharField(max_length=255, null=False)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Favorite Song added at {self.added_at}"
    
class FavoriteAlbum(models.Model):
    added_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=255, null=False)
    album_id = models.CharField(max_length=255, null=False)
    def __str__(self):
        return f"Favorite Album added at {self.added_at}"
    
class FavoritePlaylist(models.Model):
    added_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=255, null=False)
    playlist_id = models.CharField(max_length=255, null=False)
    def __str__(self):
        return f"Favorite Playlist added at {self.added_at}"
    
