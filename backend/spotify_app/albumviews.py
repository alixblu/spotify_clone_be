from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Album
from .serializers import AlbumSerializer
from bson import ObjectId
from backend.utils import SchemaFactory
from rest_framework.permissions import AllowAny, IsAuthenticated

# 1. Create Album API
@SchemaFactory.post_schema(
    request_example={
        "artist_id": "507f1f77bcf86cd799439011",
        "album_name": "Album mới",
        "artist_name": "Nghệ sĩ ABC",
        "cover_img": "https://example.com/cover.jpg",
        "release_date": "2023-01-01",
        "total_tracks": 10,
        "isfromDB": True
    },
    success_response={
        "message": "Album created successfully!",
        "data": {
            "_id": "507f1f77bcf86cd799439012",
            "artist_id": "507f1f77bcf86cd799439011",
            "album_name": "Album mới",
            "artist_name": "Nghệ sĩ ABC",
            "cover_img": "https://example.com/cover.jpg",
            "release_date": "2023-01-01",
            "total_tracks": 10,
            "isfromDB": True,
            "isHidden": False
        }
    },
    error_responses=[
        {
            "name": "Validation Error",
            "response": {
                "album_name": ["This field is required."],
                "artist_id": ["This field is required."]
            },
            "status_code": 400
        }
    ],
    description="Tạo album mới",
    request_serializer=AlbumSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def create_album(request):
    """ Create a new album """
    album_data = {
        'artist_id': request.data.get('artist_id'),
        'album_name': request.data.get('album_name'),
        'artist_name': request.data.get('artist_name'),
        'cover_img': request.data.get('cover_img', None),
        'release_date': request.data.get('release_date'),
        'total_tracks': request.data.get('total_tracks'),
        'isfromDB': request.data.get('isfromDB', True),
        'isHidden': request.data.get('isHidden', False),
    }
    
    serializer = AlbumSerializer(data=album_data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Album created successfully!", "data": serializer.data}, status=201)
    
    return Response(serializer.errors, status=400)


# 2. List Albums API
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "album_name": "Album mẫu",
        "artist_name": "Nghệ sĩ XYZ",
        "cover_img": "https://example.com/cover1.jpg",
        "release_date": "2022-01-01",
        "total_tracks": 12,
        "isHidden": False
    },
    search_fields=["album_name", "artist_name"],
    description="Lấy danh sách tất cả album",
    pagination=True,
    serializer=AlbumSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def list_albums(request):
    """ Retrieve all albums """
    albums = Album.objects.all()
    serializer = AlbumSerializer(albums, many=True)
    return Response(serializer.data)


# 3. Get Album Detail API
@SchemaFactory.retrieve_schema(
    item_id_param="album_id",
    success_response={
        "_id": "507f1f77bcf86cd799439011",
        "album_name": "Album chi tiết",
        "artist_name": "Nghệ sĩ ABC",
        "cover_img": "https://example.com/cover2.jpg",
        "release_date": "2023-05-01",
        "total_tracks": 8,
        "isHidden": False
    },
    description="Lấy thông tin chi tiết album"
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def get_album(request, album_id):
    """ Retrieve a specific album by ID """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        serializer = AlbumSerializer(album)
        return Response(serializer.data)
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)


# 4. Update Album API
@SchemaFactory.update_schema(
    item_id_param="album_id",
    request_example={
        "album_name": "Tên album mới",
        "total_tracks": 15
    },
    success_response={
        "message": "Album updated!",
        "data": {
            "_id": "507f1f77bcf86cd799439011",
            "album_name": "Tên album mới",
            "total_tracks": 15,
            # ... other fields
        }
    },
    description="Cập nhật thông tin album",
    request_serializer=AlbumSerializer
)
@api_view(['PUT'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def update_album(request, album_id):
    """ Update album details """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Album updated!", "data": serializer.data})
        return Response(serializer.errors, status=400)
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)


# 5. Delete Album API
@SchemaFactory.delete_schema(
    item_id_param="album_id",
    success_response={
        "message": "Album deleted successfully!"
    },
    description="Xóa album"
)
@api_view(['DELETE'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def delete_album(request, album_id):
    """ Delete an album """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        album.delete()
        return Response({"message": "Album deleted successfully!"})
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)