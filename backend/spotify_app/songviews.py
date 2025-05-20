from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Song, Album, Playlist
from music_library.models import PlaylistSong
from .serializers import SongSerializer
from mutagen.mp3 import MP3
from bson import ObjectId
import datetime
from io import BytesIO
from backend.utils import SchemaFactory

def format_duration(seconds):
    if seconds:
        return str(datetime.timedelta(seconds=seconds))  # Converts to hh:mm:ss
    return "00:00:00"

def get_audio_duration(audio_file):
    if not audio_file:
        return None
    try:
        file_stream = BytesIO(audio_file.read())  # Convert to in-memory stream
        audio = MP3(file_stream)  # Load MP3 without saving
        return round(audio.info.length)  # Return duration in seconds
    except Exception as e:
        print(f"DEBUG: Lỗi lấy độ dài âm thanh: {str(e)}")
        return None

# 1. Upload Song API
@SchemaFactory.post_schema(
    item_id_param=None,
    request_example={
        "title": "Bài hát mới",
        "audio_file": "<binary_file>",
        "video_file": "<binary_file>",
        "img": "https://example.com/image.jpg",
        "album_id": "507f1f77bcf86cd799439011"
    },
    success_response={
        "message": "Tải bài hát thành công!",
        "data": {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Bài hát mới",
            "duration": "00:03:45",
            "audio_file": "/media/audio/song.mp3",
            "video_file": "/media/video/song.mp4",
            "img": "https://example.com/image.jpg",
            "album_id": "507f1f77bcf86cd799439011"
        }
    },
    error_responses=[
        {
            "name": "Invalid file",
            "response": {"error": "Không nhận được file âm thanh"},
            "status_code": 400
        }
    ],
    description="Tải lên bài hát mới với file âm thanh và video",
    request_serializer=SongSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_song(request):
    print(f"DEBUG: Nhận dữ liệu yêu cầu - {request.data}")
    print(f"DEBUG: Nhận file - {request.FILES}")

    song_data = {
        'title': request.data.get('title'),
        'audio_file': request.data.get('audio_file'),
        'video_file': request.data.get('video_file'),
        'img': request.data.get('img', None),
        'album_id': request.data.get('album_id'),
        'duration': request.data.get('duration', '00:00:00'),  # Mặc định nếu không có duration
    }

    if not song_data['audio_file']:
        return Response({"error": "Không nhận được URL file âm thanh"}, status=400)

    print(f"DEBUG: Dữ liệu bài hát = {song_data}")
    serializer = SongSerializer(data=song_data, context={'request': request})
    if serializer.is_valid():
        song = serializer.save()
        print(f"DEBUG: Đã tải bài hát, _id = {song._id}")
        return Response({"message": "Tải bài hát thành công!", "data": serializer.data}, status=201)
    
    print(f"DEBUG: Lỗi xác thực - {serializer.errors}")
    return Response({"error": "Dữ liệu không hợp lệ", "details": serializer.errors}, status=400)

# 2. List Songs API
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "title": "Bài hát mẫu",
        "duration": "00:03:45",
        "audio_file": "/media/audio/song.mp3",
        "video_file": "/media/video/song.mp4",
        "img": "https://example.com/image.jpg",
        "album_id": "507f1f77bcf86cd799439011",
        "isHidden": False
    },
    description="Lấy danh sách tất cả bài hát (công khai)"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_songs(request):
    print("DEBUG: Đang lấy tất cả bài hát")
    try:
        # Tạm thời lấy tất cả bài hát và lọc isHidden trong Python
        songs = Song.objects.all()
        # Lọc các bài hát không ẩn
        visible_songs = [song for song in songs if not song.isHidden]
        serializer = SongSerializer(visible_songs, many=True)
        print(f"DEBUG: Dữ liệu bài hát = {serializer.data}")
        return Response(serializer.data)
    except Exception as e:
        print(f"DEBUG: Lỗi khi lấy danh sách bài hát: {str(e)}")
        return Response({"error": "Lỗi khi lấy danh sách bài hát", "details": str(e)}, status=500)

# 3. Get Song Detail API
@SchemaFactory.retrieve_schema(
    item_id_param="song_id",
    success_response={
        "_id": "507f1f77bcf86cd799439011",
        "title": "Bài hát mẫu",
        "duration": "00:03:45",
        "audio_file": "/media/audio/song.mp3",
        "video_file": "/media/video/song.mp4",
        "img": "https://example.com/image.jpg",
        "album_id": "507f1f77bcf86cd799439011",
        "isHidden": False
    },
    description="Lấy chi tiết của một bài hát cụ thể"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_song(request, song_id):
    print(f"DEBUG: Đang lấy bài hát với _id = {song_id}")
    if not song_id or song_id == "undefined":
        print(f"DEBUG: Song_id không hợp lệ: {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        serializer = SongSerializer(song)
        print(f"DEBUG: Dữ liệu bài hát = {serializer.data}")
        return Response(serializer.data)
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)

# 4. Get Songs by Album API
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "title": "Bài hát mẫu",
        "duration": "00:03:45",
        "audio_file": "https://cloudinary.com/audio.mp3",
        "album_id": "60d5ec9cf8a1b4626e7d4e92"
    },
    description="Lấy tất cả bài hát thuộc một album cụ thể",
    pagination=True
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_songs_by_album(request, album_id):
    print(f"DEBUG: Đang lấy bài hát cho album_id = {album_id}")
    try:
        # Lọc trong Python thay vì dùng isHidden=False
        songs = Song.objects.filter(album_id=ObjectId(album_id))
        visible_songs = [song for song in songs if not song.isHidden]
        serializer = SongSerializer(visible_songs, many=True)
        print(f"DEBUG: Bài hát trong album = {serializer.data}")
        return Response({
            "results": serializer.data,
            "count": len(serializer.data),
            "next": None,
            "previous": None
        })
    except Album.DoesNotExist:
        print(f"DEBUG: Không tìm thấy album với _id = {album_id}")
        return Response({"error": "Không tìm thấy album"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {album_id}")
        return Response({"error": "Album ID không hợp lệ"}, status=400)
    except Exception as e:
        print(f"DEBUG: Lỗi khi lấy bài hát cho album: {str(e)}")
        return Response({"error": str(e)}, status=400)

# 5. Update Song API
@SchemaFactory.update_schema(
    item_id_param="song_id",
    request_example={
        "title": "Tên bài hát mới",
        "img": "https://example.com/image.jpg",
        "audio_file": "<binary_file>",
        "video_file": "<binary_file>",
        "album_id": "507f1f77bcf86cd799439011"
    },
    success_response={
        "message": "Cập nhật bài hát thành công!",
        "data": {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Tên bài hát mới",
            "duration": "00:03:45",
            "audio_file": "/media/audio/song.mp3",
            "video_file": "/media/video/song.mp4",
            "img": "https://example.com/new_image.jpg",
            "album_id": "507f1f77bcf86cd799439011"
        }
    },
    description="Cập nhật thông tin bài hát (hỗ trợ cập nhật từng phần)",
    request_serializer=SongSerializer
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def update_song(request, song_id):
    print(f"DEBUG: Đang cập nhật bài hát với _id = {song_id}")
    print(f"DEBUG: Dữ liệu yêu cầu = {request.data}")
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        audio_blob = request.FILES.get('audio_file')
        if audio_blob:
            audio_duration = get_audio_duration(audio_blob)
            song_duration = format_duration(audio_duration) if audio_duration else "00:00:00"
            request.data['duration'] = song_duration
        serializer = SongSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(f"DEBUG: Đã cập nhật bài hát với _id = {song_id}, dữ liệu = {serializer.data}")
            return Response({"message": "Cập nhật bài hát thành công!", "data": serializer.data}, status=200)
        print(f"DEBUG: Lỗi xác thực = {serializer.errors}")
        return Response({"error": "Dữ liệu không hợp lệ", "details": serializer.errors}, status=400)
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)
    except Exception as e:
        print(f"DEBUG: Lỗi khi cập nhật bài hát: {str(e)}")
        return Response({"error": str(e)}, status=500)

# 6. Delete Song API
@SchemaFactory.delete_schema(
    item_id_params="song_id",
    success_response={
        "message": "Xóa bài hát thành công!",
        "deleted_id": "507f1f77bcf86cd799439011"
    },
    description="Xóa bài hát vĩnh viễn"
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_song(request, song_id):
    print(f"DEBUG: Đang cố xóa bài hát với _id = {song_id}")
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        song.delete()
        print(f"DEBUG: Đã xóa bài hát với _id = {song_id}")
        return Response({"message": "Xóa bài hát thành công!", "deleted_id": str(song_id)})
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)

# 7. Hide Song API
@api_view(['PUT'])
@permission_classes([AllowAny])
def hide_song(request, song_id):
    print(f"DEBUG: Đang ẩn bài hát với _id = {song_id}")
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        song.isHidden = True
        song.save()
        print(f"DEBUG: Đã ẩn bài hát, _id = {song_id}, isHidden = {song.isHidden}")
        return Response({
            "message": "Ẩn bài hát thành công!",
            "data": {"song_id": str(song._id), "isHidden": song.isHidden}
        }, status=200)
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)

# 8. Unhide Song API
@api_view(['PUT'])
@permission_classes([AllowAny])
def unhide_song(request, song_id):
    print(f"DEBUG: Đang bỏ ẩn bài hát với _id = {song_id}")
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        song.isHidden = False
        song.save()
        print(f"DEBUG: Đã bỏ ẩn bài hát, _id = {song_id}, isHidden = {song.isHidden}")
        return Response({
            "message": "Bỏ ẩn bài hát thành công!",
            "data": {"song_id": str(song._id), "isHidden": song.isHidden}
        }, status=200)
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {song_id}")
        return Response({"error": "Song ID không hợp lệ"}, status=400)

# 9. Delete Song in Album API
@SchemaFactory.delete_schema(
    item_id_params=["album_id", "song_id"],
    success_response={
        "message": "Xóa bài hát thành công!",
        "deleted_id": "507f1f77bcf86cd799439011",
        "album_id": "60d5ec9cf8a1b4626e7d4e92"
    },
    error_responses=[
        {
            "name": "Not Found",
            "response": {"error": "Không tìm thấy bài hát trong album chỉ định"},
            "status_code": 404
        },
        {
            "name": "Invalid ID",
            "response": {"error": "Định dạng song_id hoặc album_id không hợp lệ"},
            "status_code": 400
        }
    ],
    description="Xóa bài hát khỏi album cụ thể vĩnh viễn. Yêu cầu cả album_id và song_id."
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_song_inAlbum(request, album_id, song_id):
    print(f"DEBUG: Đang cố xóa bài hát với _id = {song_id} trong album = {album_id}")
    try:
        song = Song.objects.get(_id=ObjectId(song_id), album_id=ObjectId(album_id))
        song.delete()
        print(f"DEBUG: Đã xóa bài hát với _id = {song_id} trong album = {album_id}")
        return Response({
            "message": "Xóa bài hát thành công!",
            "deleted_id": song_id,
            "album_id": album_id
        })
    except Song.DoesNotExist:
        print(f"DEBUG: Không tìm thấy bài hát với _id = {song_id} trong album = {album_id}")
        print(f"DEBUG: Tất cả ID bài hát: {[str(song._id) for song in Song.objects.all()]}")
        return Response({"error": "Không tìm thấy bài hát trong album chỉ định"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho song_id = {song_id} hoặc album_id = {album_id}")
        return Response({"error": "Định dạng song_id hoặc album_id không hợp lệ"}, status=400)

# 10. Get Playlist Songs API (Lưu ý: Có thể không được sử dụng do urls.py ánh xạ đến playlist_songviews)
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "title": "Bài hát mẫu",
        "duration": "00:03:45",
        "audio_file": "/media/audio/song.mp3",
        "video_file": "/media/video/song.mp4",
        "img": "https://example.com/image.jpg",
        "album_id": "507f1f77bcf86cd799439011",
        "isHidden": False
    },
    description="Lấy tất cả bài hát trong một playlist cụ thể"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_playlist_songs(request, playlist_id):
    print(f"DEBUG: Đang lấy bài hát cho playlist_id = {playlist_id}")
    if not playlist_id or playlist_id == "undefined":
        print(f"DEBUG: Playlist_id không hợp lệ: {playlist_id}")
        return Response({"error": "Playlist ID không hợp lệ"}, status=400)
    try:
        playlist = Playlist.objects.get(_id=ObjectId(playlist_id))
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist)
        songs = [ps.song for ps in playlist_songs]
        # Lọc bài hát không ẩn
        visible_songs = [song for song in songs if not song.isHidden]
        serializer = SongSerializer(visible_songs, many=True)
        print(f"DEBUG: Bài hát trong playlist = {serializer.data}")
        return Response(serializer.data)
    except Playlist.DoesNotExist:
        print(f"DEBUG: Không tìm thấy playlist với _id = {playlist_id}")
        return Response({"error": "Không tìm thấy playlist"}, status=404)
    except ValueError:
        print(f"DEBUG: Định dạng ObjectId không hợp lệ cho {playlist_id}")
        return Response({"error": "Playlist ID không hợp lệ"}, status=400)