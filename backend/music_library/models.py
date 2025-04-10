from django.db import models

# Create your models here.
from django.db import models

class Song(models.Model):
    song_name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255, null=True, blank=True)

class Album(models.Model):
    album_name = models.CharField(max_length=255)
    created_by = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song)