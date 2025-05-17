from rest_framework import serializers
from .models import *
from music_library.models import PlaylistSong
from rest_framework.exceptions import ValidationError
from bson import ObjectId

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'

class PlaylistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['_id', 'user_id', 'name', 'cover_img', 'created_at', 'isfromDB', 'isHidden']

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'

class PlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
        # fields = ['_id', 'playlist', 'song', 'added_at']
        fields = '__all__'

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class FollowSerializer(serializers.ModelSerializer):
    follower_id = serializers.CharField()
    target_id = serializers.CharField()
    target_type = serializers.ChoiceField(choices=['user', 'artist'])

    class Meta:
        model = Follow
        fields = '__all__'
