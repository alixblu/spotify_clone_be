from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .models import Playlist, Song
from music_library.models import PlaylistSong
from .serializers import PlaylistSongSerializer
from django.utils.timezone import now
import traceback
from backend.utils import SchemaFactory

# Thêm bài hát vào playlist
@SchemaFactory.post_schema(
    request_example={
        "song_id": "507f1f77bcf86cd799439011"
    },
    success_response={
        "message": "Song added to playlist successfully",
        "playlist_song": {
            "playlist_id": "507f1f77bcf86cd799439012",
            "song_id": "507f1f77bcf86cd799439011",
            "added_at": "2023-01-01T00:00:00Z"
        }
    },
    error_responses=[
        {
            "name": "Thiếu song_id",
            "response": {"error": "Song ID is required"},
            "status_code": 400
        },
        {
            "name": "Bài hát đã tồn tại",
            "response": {"error": "Song already exists in this playlist"},
            "status_code": 400
        }
    ],
    description="Thêm bài hát vào playlist",
    request_serializer=PlaylistSongSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def add_songs_to_playlist(request, playlist_id):
    # Lấy song_id từ dữ liệu yêu cầu (POST body)
    song_id = request.data.get('song_id')

    if not song_id:
        return Response({"error": "Song ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Chuyển playlist_id và song_id thành ObjectId
    try:
        playlist_id = ObjectId(playlist_id)
        song_id = ObjectId(song_id)
    except Exception as e:
        return Response({"error": f"Invalid ObjectId format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra sự tồn tại của playlist và bài hát
    try:
        playlist = Playlist.objects.get(_id=playlist_id)
        song = Song.objects.get(_id=song_id)
    except Playlist.DoesNotExist:
        return Response({"error": "Playlist not found."}, status=status.HTTP_404_NOT_FOUND)
    except Song.DoesNotExist:
        return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra trùng lặp
    if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
        return Response({"error": "Song already exists in this playlist."}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo dữ liệu PlaylistSong trước khi khởi tạo serializer
    playlist_song_data = {
        'playlist': playlist_id,
        'song': song_id
    }
    print(f"DEBUG: PlaylistSong data - {playlist_song_data}")
    # Khởi tạo serializer với dữ liệu đã chuẩn bị
    serializer = PlaylistSongSerializer(data=playlist_song_data)

    # Kiểm tra tính hợp lệ của dữ liệu
    if serializer.is_valid():
        try:
            print(f"DEBUG: Adding song ID - {song_id} to playlist ID - {playlist_id}")
            print(f"DEBUG: serializer found - {serializer}")
            # Lưu playlist song vào cơ sở dữ liệu
            playlist_song = serializer.save()
            return Response({
                "message": "Song added to playlist successfully",
                "playlist_song": {
                    "playlist_id": str(playlist_song.playlist._id),
                    "song_id": str(playlist_song.song._id),
                    "added_at": playlist_song.added_at
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            print(f"DEBUG: Error saving serializer: {traceback.format_exc()}")
            return Response({"error": "Error saving playlist song."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        # Nếu dữ liệu không hợp lệ, trả về thông báo lỗi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Lấy danh sách bài hát trong playlist
@SchemaFactory.retrieve_schema(
    item_id_param='playlist_id',
    success_response={
        "playlist_id": "string",
        "playlist_title": "string",
        "total_songs": 0,
        "songs": [
            {
                "_id": "string",
                "title": "string",
                "artist": "string"
            }
        ]
    },
    error_responses=[
        {
            "name": "Invalid Playlist ID",
            "response": {"error": "Invalid playlist ID format"},
            "status_code": 400
        },
        {
            "name": "Playlist Not Found",
            "response": {"error": "Playlist not found"},
            "status_code": 404
        }
    ],
    description="Lấy tổng số bài hát trong playlist",
    serializer=PlaylistSongSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_songs_in_playlist(request, playlist_id):
    try:
        # Validate playlist_id
        if not ObjectId.is_valid(playlist_id):
            return Response({"error": "Invalid playlist ID format"}, status=status.HTTP_400_BAD_REQUEST)

        playlist_obj_id = ObjectId(playlist_id)

        # Check if playlist exists
        playlist = Playlist.objects.get(_id=playlist_obj_id)
        
        # Get all songs in playlist
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist_obj_id).select_related('song')
        total_songs = playlist_songs.count()
        
        # Prepare songs data
        songs_data = []
        for ps in playlist_songs:
            song = ps.song
            songs_data.append({
                "_id": str(song._id),
                "album_id": str(song.album_id_id),
                "title": song.title,
                "duration": str(song.duration),
                "video_file": str(song.video_file) if song.video_file else None,
                "audio_file": str(song.audio_file) if song.audio_file else None,
                "img": str(song.img) if song.img else None,
                "isfromDB": song.isfromDB,
                "created_at": song.created_at,
                "isHidden": song.isHidden,
            })

        response_data = {
            "success": True,
            "playlist_id": str(playlist._id),
            "user_id": str(playlist.user_id),
            "playlist_title": playlist.name,
            "image": str(playlist.cover_img),
            "total_songs": total_songs,
            "songs": songs_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Playlist.DoesNotExist:
        return Response({"error": "Playlist not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(
            {"error": "An error occurred while processing your request"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )