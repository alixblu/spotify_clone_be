# Create your views here.
##########

from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from spotify_app.permissionsCustom import IsAdminUser
from .models import Song, Album
from .serializers import SongSerializer
from mutagen.mp3 import MP3
from bson import ObjectId
from django.core.exceptions import ValidationError
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

    file_stream = BytesIO(audio_file.read())  # Convert to in-memory stream
    audio = MP3(file_stream)  # Load MP3 without saving
    return round(audio.info.length)  # Return duration in seconds

# schema cho api upload song
# 1. Upload Song API
@SchemaFactory.post_schema(
    item_id_param= None,
    request_example={
        "title": "Bài hát mới",
        "audio_file": "<binary_file>",
        "video_file": "<binary_file>",
        "img": "https://example.com/image.jpg",
        "album_id": "507f1f77bcf86cd799439011"
    },
    success_response={
        "message": "Song uploaded successfully!",
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
            "response": {"error": "No audio or video file received"},
            "status_code": 400
        }
    ],
    description="Upload a new song with audio and video files",
    request_serializer=SongSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_song(request):
    # print(f"DEBUG: Received request data - {request.data}")
    # print(f"DEBUG: Received files - {request.FILES}")

    audio_blob = request.FILES.get('audio_file')
    video_blob = request.FILES.get('video_file')
    # image_blob = request.FILES.get('img')

    # print(f"DEBUG: audio_file received - {audio_blob}")
    # print(f"DEBUG: video_file received - {video_blob}")

    if not audio_blob or not video_blob:
        return Response({"error": "No audio or video file received"}, status=400)

    # Process duration
    audio_duration = get_audio_duration(audio_blob) if audio_blob else None
    song_duration = format_duration(audio_duration)
    # 2. Xử lý album_id
    album_id = request.data.get('album_id')
    album = None
    if album_id:
        try:
            album = Album.objects.get(_id=album_id)
        except (Album.DoesNotExist, ValueError):
            return Response({"error": "Invalid album_id"}, status=400)

    song_data = {
        'title': request.data.get('title'),
        'duration': song_duration,
        'audio_file': audio_blob,
        'video_file': video_blob,
        'img': request.data.get('img', None),
        'album_id': request.data.get('album_id', None),
    }

    serializer = SongSerializer(data=song_data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Song uploaded successfully!", "data": serializer.data}, status=201)
    
    print(f"DEBUG: Validation Errors - {serializer.errors}")
    return Response(serializer.errors, status=400)


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
    description="Get list of all songs (public)"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_songs(request):
    songs = Song.objects.all()
    serializer = SongSerializer(songs, many=True)
    return Response(serializer.data)


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
    description="Get details of a specific song"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_song(request, song_id):
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        serializer = SongSerializer(song)
        return Response(serializer.data)
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    
from rest_framework.response import Response
from bson import ObjectId


# Lấy bài hat trong album
@SchemaFactory.list_schema(
    item_example={  # Truyền item_example thay vì success_response
        "_id": "507f1f77bcf86cd799439011",
        "title": "Bài hát mẫu",
        "duration": "00:03:45",
        "audio_file": "https://cloudinary.com/audio.mp3",
        "album_id": "60d5ec9cf8a1b4626e7d4e92"
    },
    description="Get all songs belonging to a specific album",
    pagination=True  # Bật phân trang nếu cần
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_songs_by_album(request, album_id):
    try:
        songs = Song.objects.filter(album_id=ObjectId(album_id), isHidden=False)
        serializer = SongSerializer(songs, many=True)
        
        return Response({
            "results": serializer.data,  # Khớp với cấu trúc trong item_example
            "count": len(serializer.data),
            "next": None,
            "previous": None
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=400)

# 4. Update Song API
@SchemaFactory.update_schema(
    item_id_param="song_id",
    request_example={
        "title": "Tên bài hát mới",
        "img": "https://example.com/image.jpg"
    },
    success_response={
        "message": "Song updated!",
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
    description="Update song information (partial update supported)",
    request_serializer=SongSerializer
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAdminUser])
def update_song(request, song_id):
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        # image_blob = request.FILES.get('img')  # Nhận file từ request

        # # Nếu có file ảnh mới, upload lên Cloudinary
        # if image_blob:
        #     song.img = image_blob

        # Cập nhật các trường khác
        serializer = SongSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Song updated!", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)

    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

# 5. Delete Song API
@SchemaFactory.delete_schema(
    item_id_params="song_id",
    success_response={
        "message": "Song deleted successfully!",
        "deleted_id": "507f1f77bcf86cd799439011"
    },
    description="Delete a song permanently"
)    
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_song(request, song_id):
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        song.delete()
        return Response({"message": "Song deleted successfully!"})
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)


# 6. Hide Song API
@SchemaFactory.update_schema(
    item_id_param="song_id",
    success_response={
        "message": "Song hidden successfully!",
        "data": {
            "song_id": "507f1f77bcf86cd799439011",
            "isHidden": True
        }
    },
    description="Hide a song (mark as not visible to public)"
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def hide_song(request, song_id):
    try:
        # Ensure song_id is valid
        try:
            song = Song.objects.get(_id=ObjectId(song_id))
        except (Song.DoesNotExist, ValueError):
            return Response({"error": "Invalid Song ID or Song not found"}, status=404)

        # Update the song's visibility
        song.isHidden = True
        song.save()

        return Response({"message": "Song hidden successfully!", "data": {"song_id": str(song._id), "isHidden": song.isHidden}}, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debugging log
        return Response({"error": "Internal Server Error"}, status=500)


# 7. Unhide Song API
@SchemaFactory.update_schema(
    item_id_param="song_id",
    success_response={
        "message": "Song unhidden successfully!",
        "data": {
            "song_id": "507f1f77bcf86cd799439011",
            "isHidden": False
        }
    },
    description="Unhide a song (mark as visible to public)"
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def unhide_song(request, song_id):
    try:
        # Ensure song_id is valid
        try:
            song = Song.objects.get(_id=ObjectId(song_id))
        except (Song.DoesNotExist, ValueError):
            return Response({"error": "Invalid Song ID or Song not found"}, status=404)

        # Update the song's visibility
        song.isHidden = False
        song.save()

        return Response({"message": "Song unhidden successfully!", "data": {"song_id": str(song._id), "isHidden": song.isHidden}}, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")


# Xóa bài hát trong album
@SchemaFactory.delete_schema(
    item_id_params=["album_id", "song_id"],  # Thay đổi thành danh sách các param
    success_response={
        "message": "Song deleted successfully!",
        "deleted_id": "507f1f77bcf86cd799439011",
        "album_id": "60d5ec9cf8a1b4626e7d4e92"  # Thêm album_id vào response mẫu
    },
    error_responses=[
        {
            "name": "Not Found",
            "response": {"error": "Song not found in specified album"},
            "status_code": 404
        },
        {
            "name": "Invalid ID",
            "response": {"error": "Invalid song_id or album_id format"},
            "status_code": 400
        }
    ],
    description="Delete a song from specific album permanently. Requires both album_id and song_id."
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_song_inAlbum(request, album_id, song_id):
    try:
        song = Song.objects.get(
            _id=ObjectId(song_id),
            album_id=ObjectId(album_id)  # Kiểm tra song thuộc album
        )
        song.delete()
        return Response({
            "message": "Song deleted successfully!",
            "deleted_id": song_id,
            "album_id": album_id  # Trả về cả album_id
        })
    except Song.DoesNotExist:
        return Response(
            {"error": "Song not found in specified album"}, 
            status=404
        )
    except ValueError:
        return Response(
            {"error": "Invalid song_id or album_id format"},
            status=400
        )