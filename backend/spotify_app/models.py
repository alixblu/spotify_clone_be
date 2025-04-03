from djongo import models

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    duration = models.IntegerField()
    spotify_id = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.CharField(max_length=255)  # Replace with a ForeignKey to your User model if you use authentication
    songs = models.ArrayReferenceField(
        to=Song,
        on_delete=models.CASCADE,
    )