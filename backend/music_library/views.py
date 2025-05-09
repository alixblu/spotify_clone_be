from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .models import ArtistPerform, Artist, Song
from music_library.serializers import ArtistPerformSerializer
from backend.utils import SchemaFactory
import traceback

@SchemaFactory.post_schema(
        item_id_param="artist_id",
        request_example={
            "song_id": "663bb2f9e0d4f142c6f51499"
        },
        success_response={
            "message": "Thêm nghệ sĩ biểu diễn bài hát thành công",
            "artist_perform": {
                "_id": "663bb309e0d4f142c6f5149a",
                "artist_id": "663bb2e3e0d4f142c6f51498",
                "song_id": "663bb2f9e0d4f142c6f51499"
            }
        },
        error_responses= None,
        description="Thêm nghệ sĩ biểu diễn bài hát.",
        request_serializer=ArtistPerformSerializer,  
        response_serializer = None,
    )
@api_view(['POST'])
@permission_classes([AllowAny])
def add_artist_performance(request, artist_id):
    # Lấy song_id từ dữ liệu yêu cầu (POST body)
    song_id = request.data.get('song_id')

    if not song_id:
        return Response({"error": "Song ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Chuyển artist_id và song_id thành ObjectId
    try:
        artist_id = ObjectId(artist_id)
        song_id = ObjectId(song_id)
    except Exception as e:
        return Response({"error": f"Invalid ObjectId format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra sự tồn tại của artist và bài hát
    try:
        artist = Artist.objects.get(_id=artist_id)
        song = Song.objects.get(_id=song_id)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found."}, status=status.HTTP_404_NOT_FOUND)
    except Song.DoesNotExist:
        return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra trùng lặp
    if ArtistPerform.objects.filter(artist_id=artist, song_id=song).exists():
        return Response({"error": "Nghệ sĩ đã biểu diễn bài hát này."}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo dữ liệu ArtistPerform
    artist_perform_data = {
        'artist_id': artist_id,
        'song_id': song_id
    }

    # Khởi tạo serializer
    serializer = ArtistPerformSerializer(data=artist_perform_data)

    # Kiểm tra tính hợp lệ của dữ liệu
    if serializer.is_valid():
        try:
            # Lưu vào cơ sở dữ liệu
            artist_perform = serializer.save()
            return Response({
                "message": "Thêm nghệ sĩ biểu diễn bài hát thành công",
                "artist_perform": {
                    "artist_id": str(artist_perform.artist_id),
                    "song_id": str(artist_perform.song_id),
                    "_id": str(artist_perform._id)
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"DEBUG: Error saving serializer: {traceback.format_exc()}")
            return Response({"error": "Error saving artist performance."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Nếu dữ liệu không hợp lệ, trả về thông báo lỗi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
