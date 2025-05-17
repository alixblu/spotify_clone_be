from rest_framework import serializers
from music_library.models import ArtistPerform, Song, Artist, FavoriteSong, FavoriteAlbum
from spotify_app.serializers import SongSerializer  # Import SongSerializer

# =========================================  ARTISTPERFORM  ========================================
class SongNestedSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['_id', 'title', 'duration', 'album_id']

    def get__id(self, obj):
        return str(obj._id)


class ArtistNestedSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['_id', 'artist_name']

    def get__id(self, obj):
        return str(obj._id)

# Dùng để lấy danh sách theo id bài hát 
class ArtistPerformBySongSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField()
    artist = ArtistNestedSerializer(read_only=True)
    song = SongNestedSerializer(read_only=True)

    class Meta:
        model = ArtistPerform
        fields = ['_id', 'artist', 'song']

    def get__id(self, obj):
        return str(obj._id)
# Dùng để lấy danh sách theo id nghệ sĩ
class ArtistPerformByArtistSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField()
    artist_id = serializers.SerializerMethodField()
    song = SongNestedSerializer(read_only=True)

    class Meta:
        model = ArtistPerform
        fields = ['_id', 'artist_id', 'song']

    def get__id(self, obj):
        return str(obj._id)

    def get_artist_id(self, obj):
        return str(obj.artist._id) if obj.artist else None


class ArtistPerformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistPerform
        fields = '__all__'


# ========================================= FAVORITE SONG ========================================
class FavoriteSongSerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)
    
    class Meta:
        model = FavoriteSong
        fields = ['user_id', 'song', 'added_at']
        extra_kwargs = {
            'user_id': {'read_only': True},
            'added_at': {'read_only': True}
        }

# class FavoriteSongCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FavoriteSong
#         fields = '__all__'
class FavoriteSongCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteSong
        fields = ['_id', 'user', 'song', 'added_at']
        read_only_fields = ['_id', 'added_at']


#========================================== FAVORITE ALBUM ========================================
class FavoriteAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteAlbum
        fields = '__all__'


#========================================= FAVORITE PLAYLIST ========================================
class FavoritePlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteAlbum
        fields = '__all__'