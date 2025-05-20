from rest_framework import serializers
from .models import Song, Album, Artist, Playlist, Follow
from music_library.models import PlaylistSong
from bson import ObjectId

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
        read_only_fields = ['_id', 'artist_name']

    def validate_artist(self, value):
        print(f"DEBUG: Validating artist: {value}, type: {type(value)}")
        if not isinstance(value, str):
            raise serializers.ValidationError("Artist ID must be a string.")
        try:
            artist = Artist.objects.get(_id=ObjectId(value))
            return artist
        except Artist.DoesNotExist:
            print(f"DEBUG: Artist with ID {value} not found")
            raise serializers.ValidationError("Invalid or non-existent artist ID.")
        except ValueError:
            print(f"DEBUG: Invalid ObjectId format for artist ID: {value}")
            raise serializers.ValidationError("Artist ID must be a valid ObjectId.")

    def validate_release_date(self, value):
        print(f"DEBUG: Validating release_date: {value}, type: {type(value)}")
        return value

    def validate_total_tracks(self, value):
        print(f"DEBUG: Validating total_tracks: {value}, type: {type(value)}")
        if value < 0:
            raise serializers.ValidationError("Total tracks cannot be negative.")
        return value

    def create(self, validated_data):
        artist = validated_data['artist']
        validated_data['artist_name'] = artist.artist_name
        print(f"DEBUG: Creating album with validated_data: {validated_data}")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        artist = validated_data.get('artist', instance.artist)
        validated_data['artist_name'] = artist.artist_name
        print(f"DEBUG: Updating album with validated_data: {validated_data}")
        return super().update(instance, validated_data)

class SongSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True, source='album_id')
    album_id = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Song
        fields = '__all__'

    def validate_album_id(self, value):
        print(f"DEBUG: Validating album_id: {value}")
        if value:
            try:
                object_id = ObjectId(value)
                album = Album.objects.get(_id=object_id)
                print(f"DEBUG: Found album: {album}, album_name: {album.album_name}")
                return value
            except Album.DoesNotExist:
                print(f"DEBUG: Album with ID {value} not found")
                all_albums = Album.objects.all()
                print(f"DEBUG: All albums: {[str(album._id) for album in all_albums]}")
                raise serializers.ValidationError(f"Album with ID {value} does not exist")
            except ValueError:
                print(f"DEBUG: Invalid ObjectId format for album_id: {value}")
                raise serializers.ValidationError("album_id must be a valid ObjectId")
        return value

    def create(self, validated_data):
        album_id = validated_data.pop('album_id', None)
        log_data = validated_data.copy()
        log_data['album_id'] = album_id
        if album_id:
            try:
                album = Album.objects.get(_id=ObjectId(album_id))
                validated_data['album_id'] = album
            except (Album.DoesNotExist, ValueError):
                print(f"DEBUG: Invalid or non-existent album_id: {album_id}")
                validated_data['album_id'] = None
        else:
            validated_data['album_id'] = None
        print(f"DEBUG: Creating song with validated_data: {log_data}")
        return Song.objects.create(**validated_data)

    def update(self, instance, validated_data):
        album_id = validated_data.pop('album_id', None)
        if album_id:
            try:
                album = Album.objects.get(_id=ObjectId(album_id))
                validated_data['album_id'] = album
            except (Album.DoesNotExist, ValueError):
                print(f"DEBUG: Invalid or non-existent album_id: {album_id}")
                validated_data['album_id'] = instance.album_id
        else:
            validated_data['album_id'] = instance.album_id
        print(f"DEBUG: Updating song with validated_data: {validated_data}")
        return super().update(instance, validated_data)

class PlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
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