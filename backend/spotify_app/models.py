from django.db import models

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    cover_img = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Artist(models.Model):
    artist_name = models.CharField(max_length=255)
    profile_img = models.URLField(null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    label = models.CharField(max_length=50, default="Artist")
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.artist_name

class Album(models.Model):
    album_name = models.CharField(max_length=255)
    artist_id = models.CharField(max_length=255, null=True, blank=True)
    artist_name = models.CharField(max_length=255, null=True, blank=True)
    cover_img = models.URLField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    total_tracks = models.IntegerField(default=0)
    isfromDB = models.BooleanField(default=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.album_name
    
class Song(models.Model):
    title = models.CharField(max_length=255)
    album_id = models.CharField(max_length=255, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    video_file = models.BinaryField(null=True, blank=True)
    audio_file = models.BinaryField(null=True, blank=True)
    img = models.URLField(null=True, blank=True)
    isfromDB = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isHidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
