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
    release_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])  # Chuyển chuỗi thành date
    cover_img = serializers.URLField(allow_blank=True, allow_null=True)  # Khớp với URLField

    class Meta:
        model = Album
        fields = ['_id', 'artist', 'album_name', 'artist_name', 'release_date', 
                 'total_tracks', 'isfromDB', 'isHidden', 'cover_img']
        read_only_fields = ['_id']

    def validate_artist(self, value):
        print("Validating artist:", value, type(value))
        if not isinstance(value, str):
            raise serializers.ValidationError("ID nghệ sĩ phải là chuỗi.")
        try:
            # Chuyển ObjectId thành instance Artist
            artist = Artist.objects.get(_id=ObjectId(value))
            return artist  # Trả về instance Artist
        except (Artist.DoesNotExist, ValueError):
            raise serializers.ValidationError("ID nghệ sĩ không hợp lệ hoặc không tồn tại.")

    def validate_release_date(self, value):
        print("Validating release_date:", value, type(value))
        # value đã là datetime.date do DateField xử lý
        return value

    def validate_total_tracks(self, value):
        print("Validating total_tracks:", value, type(value))
        if value < 0:
            raise serializers.ValidationError("Số lượng bài hát không thể âm.")
        return value

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
