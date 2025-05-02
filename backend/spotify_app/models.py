from djongo import models
from bson import ObjectId

from user_management.models import User

class Playlist(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, auto_created=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cover_img = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isfromDB = models.BooleanField(default=True)  
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "playlists"
    def __str__(self):
        return self.name
    
class Artist(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    artist_name = models.CharField(max_length=255)
    profile_img = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True)
    label = models.CharField(max_length=50, default="Artist")
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "artists"
    def __str__(self):
        return self.artist_name
    
class Album(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    cover_img = models.URLField(blank=True, null=True)
    release_date = models.DateField()
    total_tracks = models.IntegerField()
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "albums"

    def __str__(self):
        return self.album_name
    
class Song(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId, auto_created=True)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    duration = models.TimeField()
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    audio_file = models.FileField(upload_to='audios/', blank=True, null=True)
    img = models.URLField(blank=True, null=True)
    isfromDB = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isHidden = models.BooleanField(default=False)

    class Meta:
        db_table = "songs"
    def __str__(self):
        return self.title
    
