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
    artist = serializers.CharField()  # Nhận chuỗi ObjectId
    release_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    cover_img = serializers.URLField(allow_blank=True, allow_null=True)

    class Meta:
        model = Album
        fields = ['_id', 'artist', 'album_name', 'artist_name', 'release_date', 
                 'total_tracks', 'isfromDB', 'isHidden', 'cover_img']
        read_only_fields = ['_id', 'artist_name']  # Đặt artist_name là read-only

    def validate_artist(self, value):
        print("Validating artist:", value, type(value))
        if not isinstance(value, str):
            raise serializers.ValidationError("ID nghệ sĩ phải là chuỗi.")
        try:
            artist = Artist.objects.get(_id=ObjectId(value))
            return artist  # Trả về instance Artist
        except (Artist.DoesNotExist, ValueError):
            raise serializers.ValidationError("ID nghệ sĩ không hợp lệ hoặc không tồn tại.")

    def validate_release_date(self, value):
        print("Validating release_date:", value, type(value))
        return value

    def validate_total_tracks(self, value):
        print("Validating total_tracks:", value, type(value))
        if value < 0:
            raise serializers.ValidationError("Số lượng bài hát không thể âm.")
        return value

    def create(self, validated_data):
        artist = validated_data['artist']
        validated_data['artist_name'] = artist.artist_name  # Gán artist_name từ Artist
        return super().create(validated_data)

    def update(self, instance, validated_data):
        artist = validated_data.get('artist', instance.artist)
        validated_data['artist_name'] = artist.artist_name  # Cập nhật artist_name từ Artist
        return super().update(instance, validated_data)

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
