# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import status
# from bson import ObjectId
# from django.core.exceptions import ValidationError
# from .models import Playlist, Song
# from music_library.models import PlaylistSong
# from rest_framework.permissions import AllowAny

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def add_songs_to_playlist(request, playlist_id):
#     try:
#         # Validate playlist_id
#         playlist_id = ObjectId(playlist_id)
#         playlist = Playlist.objects.get(_id=playlist_id)
#         print(f"DEBUG: Playlist found - {playlist}")
#     except (Playlist.DoesNotExist, ValueError):
#         return Response({"error": "Playlist not found or invalid ID"}, status=status.HTTP_404_NOT_FOUND)

#     song_ids = request.data.get('song_ids', [])
#     if not isinstance(song_ids, list):
#         return Response({"error": "song_ids must be a list"}, status=status.HTTP_400_BAD_REQUEST)

#     added_songs = []
#     errors = []
#     # Cho thêm 1 lần nhiều bài hát vào playlist, nhưng hiện tại đang lỗi chỉ thêm được 1 bài mỗi lần
#     for song_id in song_ids:
#         try:
#             print(f"DEBUG: Adding song ID - {song_id}")
#             song_id_obj = ObjectId(song_id)
#             song = Song.objects.get(_id=song_id_obj)
#             print(f"DEBUG: Song found - {song}")
#             # Sử dụng get_or_create để tránh lỗi duplicate
#             playlist_song, created = PlaylistSong.objects.get_or_create(
#                 playlist=playlist,
#                 song=song
#             )
            
#             if created:
#                 added_songs.append(str(song_id))
#             else:
#                 errors.append(f"Song {song_id} already exists in playlist")
#             print(f"DEBUG: added_songs created - {added_songs}")
#         except (Song.DoesNotExist, ValueError) as e:
#             errors.append(f"Invalid song ID {song_id}: {str(e)}")
#             continue
#         except Exception as e:
#             errors.append(f"Error adding song {song_id}: {str(e)}")
#             continue

#     response_data = {
#         "added_count": len(added_songs),
#         "added_songs": added_songs,
#         "errors": errors,
#         "message": f"Successfully added {len(added_songs)} songs" if added_songs else "No songs were added"
#     }

#     return Response(response_data, status=status.HTTP_200_OK if added_songs else status.HTTP_207_MULTI_STATUS)




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
