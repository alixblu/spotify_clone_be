from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from spotify_app.permissionsCustom import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .models import Artist
from .serializers import ArtistSerializer
from backend.utils import SchemaFactory
from rest_framework.parsers import MultiPartParser, FormParser

# Lấy danh sách nghệ sĩ
@SchemaFactory.list_schema(
    item_example={
        "id": 1,
        "artist_name": "Sơn Tùng",
        "profile_img": "https://...",
        "biography": "Ca sĩ nổi tiếng...",
        "label": "MTP",
        "isfromDB": True,
        "isHidden": False
    },
    search_fields=["artist_name", "label"],
    description="Danh sách nghệ sĩ",
    serializer=ArtistSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_artists(request):
    artists = Artist.objects.all()
    serializer = ArtistSerializer(artists, many=True)
    return Response({
        "count": artists.count(),
        "next": None,
        "previous": None,
        "results": serializer.data
    })


# Tạo nghệ sĩ mới
@SchemaFactory.post_schema(
    request_example={
        "artist_name": "Sơn Tùng M-TP",
        "profile_img": "<file>",  # Thay đổi thành file để Swagger hiểu
        "biography": "Một ca sĩ Việt Nam...",
        "label": "MTP Entertainment",
        "isfromDB": True,
        "isHidden": False
    },
    success_response={"message": "Artist created successfully"},
    error_responses=[{
        "name": "Dữ liệu không hợp lệ",
        "response": {"error": "Invalid data"},
        "status_code": 400
    }],
    description="Tạo nghệ sĩ mới",
    request_serializer=ArtistSerializer,
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_artist(request):
    serializer = ArtistSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Thêm bước kiểm tra file
            if 'profile_img' in request.FILES:
                print("File info:", request.FILES['profile_img'].name, request.FILES['profile_img'].size)
            
            artist = serializer.save()
            print("Saved successfully. Image URL:", artist.profile_img.url)
            return Response(
                {"message": "Artist created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Log toàn bộ traceback
            import traceback
            traceback.print_exc()  # In ra console
            return Response(
                {"error": f"Failed to save artist: {str(e)}"},  # Trả về lỗi chi tiết
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Cập nhật nghệ sĩ
@SchemaFactory.post_schema(
    request_example={
        "artist_name": "Sơn Tùng M-TP Updated"
    },
    success_response={"message": "Artist updated successfully"},
    description="Cập nhật nghệ sĩ",
    request_serializer=ArtistSerializer
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_artist(request, artist_id):
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ArtistSerializer(artist, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"message": "Artist updated successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Error updating artist"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Xóa nghệ sĩ
@SchemaFactory.delete_schema(
    success_response={"message": "Artist deleted successfully"},
    description="Xóa nghệ sĩ"
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_artist(request, artist_id):
    try:
        artist = Artist.objects.get(id=artist_id)
        artist.delete()
        return Response({"message": "Artist deleted successfully"}, status=status.HTTP_200_OK)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({"error": "Error deleting artist"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
