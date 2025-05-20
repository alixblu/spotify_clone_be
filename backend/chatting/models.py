from djongo import models
from django.utils import timezone
from user_management.models import User
from music_library.models import *
from spotify_app.models import Song

class ChatRoom(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ArrayReferenceField(
        to=User,
        on_delete=models.CASCADE,default=list, related_name='joined_rooms'
    )
    song_list = models.ArrayReferenceField(
        to=Song,
        on_delete=models.CASCADE,default=list, related_name='room_playlist'
    )
    playing_song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True)
    current_time = models.FloatField(default=0.0)
    play_started_at = models.DateTimeField(null=True, blank=True)
    ban_list = models.ArrayReferenceField(
        to=User,
        on_delete=models.CASCADE,
        related_name='banned_users',
        default=list
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "chat_rooms"

class Message(models.Model):
    _id = models.ObjectIdField(primary_key=True, auto_created=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


    class Meta:
        db_table = "messages"
        ordering = ['-created_at']  # Most recent messages first

