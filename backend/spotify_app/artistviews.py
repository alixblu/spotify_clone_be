from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from spotify_app.permissionsCustom import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .models import Artist, Album
from .serializers import ArtistSerializer, AlbumSerializer
from backend.utils import SchemaFactory
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import LimitOffsetPagination
import logging

logger = logging.getLogger(__name__)

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


# Get Artist Detail API: Lấy thông tin nghệ sĩ theo ID
@SchemaFactory.retrieve_schema(
    item_id_param="artist_id",
    success_response={
        "_id": "507f1f77bcf86cd799439011",
        "artist_name": "Sơn Tùng",
        "profile_img": "https://example.com/image.jpg",
        "biography": "Ca sĩ nổi tiếng...",
        "label": "MTP Entertainment",
        "isfromDB": True,
        "isHidden": False,
        "genres": ["Pop", "V-Pop"],
        "social_links": {
            "facebook": "https://facebook.com/sontungmtp",
            "youtube": "https://youtube.com/sontungmtp"
        }
    },
    description="Lấy thông tin nghệ sĩ theo ID"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_artist_by_id(request, artist_id):
    try:
        # Validate and convert artist_id to ObjectId
        artist = Artist.objects.get(_id=ObjectId(artist_id))
        
        # Check if artist is hidden (only show to admin)
        if artist.isHidden and not request.user.is_staff:
            return Response({"error": "Artist not found"}, status=404)
        
        serializer = ArtistSerializer(artist)
        return Response(serializer.data)
    
    except (Artist.DoesNotExist, ValueError):
        return Response({"error": "Artist not found"}, status=404)
    except Exception as e:
        print(f"Error fetching artist: {str(e)}")
        return Response({"error": "Internal server error"}, status=500)


# Tạo nghệ sĩ mới
@SchemaFactory.post_schema(
    request_example={
        "artist_name": "Sơn Tùng M-TP",
        "profile_img": "https://example.com/image.jpg",  # Thay đổi thành file để Swagger hiểu
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
def create_artist(request):
    try:
        # 1. Lấy dữ liệu từ request (không dùng MultiPartParser)
        data = request.data
        
        # 2. Validate dữ liệu
        serializer = ArtistSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation error", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Lưu artist (chỉ lưu URL)
        artist = serializer.save()
        
        return Response(
            {
                "message": "Artist created successfully",
                "data": {
                    "id": str(artist._id),
                    "artist_name": artist.artist_name,
                    "profile_img": artist.profile_img  # URL từ client
                }
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating artist: {str(e)}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    
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


# Lấy danh sách album của nghệ sĩ
@SchemaFactory.list_schema(
    item_example={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "album_name": "Album mẫu",
        "artist_id": "507f1f77bcf86cd799439011",
        "cover_img": "https://example.com/cover.jpg",
        "release_date": "2023-01-01",
        "total_tracks": 10,
        "isHidden": False
    },
    description="Lấy tất cả album của nghệ sĩ theo artist_id",
    search_fields=["album_name", "release_date"],  # Các trường có thể filter
    pagination=True  # Bật phân trang
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_artist_albums(request, artist_id):
    try:
        # Validate artist_id format
        ObjectId(artist_id)
        
        # Base queryset
        albums = Album.objects.filter(artist_id=ObjectId(artist_id), isHidden=False)
        
        # Apply search filters if provided
        if 'album_name' in request.GET:
            albums = albums.filter(album_name__icontains=request.GET['album_name'])
        if 'release_date' in request.GET:
            albums = albums.filter(release_date=request.GET['release_date'])
        
        # Phân trang
        paginator = LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(albums, request, view=None)
        serializer = AlbumSerializer(paginated_queryset, many=True)
        # Trả về response phân trang
        return paginator.get_paginated_response({
            "success": True,
            "message": "User list retrieved successfully",
            "data": serializer.data
        })
        
    except ValueError:
        return Response({"error": "Invalid artist_id format"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    


# Hide artist API
@SchemaFactory.update_schema(
    item_id_param="_id",
    success_response={
        "message": "Artist hidden successfully!",
        "data": {
            "artist_id": "507f1f77bcf86cd799439011",
            "isHidden": True
        }
    },
    description="Hide an artist (mark as not visible to public)"
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def hide_artist(request, _id):
    try:
        # Ensure artist_id is valid
        try:
            artist = Artist.objects.get(_id=ObjectId(_id))
        except (Artist.DoesNotExist, ValueError):
            return Response({"error": "Invalid Artist ID or Artist not found"}, status=404)

        # Update the artist's visibility
        artist.isHidden = True
        artist.save()

        return Response({
            "message": "Artist hidden successfully!", 
            "data": {
                "artist_id": str(artist._id), 
                "isHidden": artist.isHidden
            }
        }, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debugging log
        return Response({"error": "Internal Server Error"}, status=500)



# Unhide Artist API
@SchemaFactory.update_schema(
    item_id_param="_id",
    success_response={
        "message": "Artist unhidden successfully!",
        "data": {
            "artist_id": "507f1f77bcf86cd799439011",
            "isHidden": False
        }
    },
    description="Unhide an artist (mark as visible to public)"
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def unhide_artist(request, _id):
    try:
        # Ensure artist_id is valid
        try:
            artist = Artist.objects.get(_id=ObjectId(_id))
        except (Artist.DoesNotExist, ValueError):
            return Response({"error": "Invalid Artist ID or Artist not found"}, status=404)

        # Update the artist's visibility
        artist.isHidden = False
        artist.save()

        return Response({
            "message": "Artist unhidden successfully!", 
            "data": {
                "artist_id": str(artist._id), 
                "isHidden": artist.isHidden
            }
        }, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debugging log
        return Response({"error": "Internal Server Error"}, status=500)