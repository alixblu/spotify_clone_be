from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Album, Artist
from .serializers import AlbumSerializer
from bson import ObjectId
from bson.errors import InvalidId
from backend.utils import SchemaFactory
from rest_framework.permissions import AllowAny, IsAuthenticated
from spotify_app.permissionsCustom import IsAdminUser

# 1. Create Album API
@SchemaFactory.post_schema(
    request_example={
        "artist": "507f1f77bcf86cd799439011",
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
@permission_classes([IsAdminUser])  # Chỉ cho phép admin tạo album
def create_album(request):
    """ 
    Create a new album
    Required fields: artist_id, album_name, release_date
    """
    try:
        # 1. Kiểm tra các trường bắt buộc
        required_fields = ['artist', 'album_name', 'release_date']
        for field in required_fields:
            if field not in request.data or not request.data.get(field):
                return Response(
                    {"error": f"Trường '{field}' là bắt buộc."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Kiểm tra artist_id có hợp lệ không và có tồn tại không
        artist_id = request.data['artist']
        print(f"DEBUG: Nhận artist_id - {artist_id}")

        try:
            artist_obj = Artist.objects.get(_id=ObjectId(artist_id))
            print(f"DEBUG: Tìm thấy Artist - {artist_obj}")
        except (Artist.DoesNotExist, InvalidId):
            return Response(
                {"error": "Invalid artist_id or artist not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        print(f"DEBUG: artist_obj - {artist_obj._id}")
        # 3. Chuẩn bị dữ liệu album
        album_data = {
            'artist': ObjectId(artist_obj._id),  # Nếu AlbumSerializer yêu cầu chuỗi
            'album_name': request.data['album_name'].strip(),
            'artist_name': request.data.get('artist_name', '').strip() or artist_obj.name,  # fallback nếu không có
            'cover_img': request.data.get('cover_img'),
            'release_date': request.data['release_date'],
            'total_tracks': int(request.data.get('total_tracks', 0)),
            'isfromDB': bool(request.data.get('isfromDB', True)),
            'isHidden': bool(request.data.get('isHidden', False)),
        }

        # 4. Validate và lưu dữ liệu
        serializer = AlbumSerializer(data=album_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Album created successfully!",
                    # "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        # Nếu không hợp lệ, trả về lỗi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": f"Lỗi hệ thống: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
        # Chuyển album_id thành ObjectId (nếu hợp lệ)
        object_id = ObjectId(album_id)
        print(f"DEBUG: Nhận object_id - {object_id}")
    except InvalidId:
        return Response(
            {"error": "Invalid album ID format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        album = Album.objects.get(_id=object_id)
        print(f"DEBUG: Tìm thấy Album - {album}")
        alserializer = AlbumSerializer(album)
        data = alserializer.data
        # Chuyển tất cả ObjectId thành string (nếu có)
        data['_id'] = str(album._id)
        print(f"DEBUG: album._id - {album._id}")
        print(f"DEBUG: data['_id'] - {data['_id']}")
        print(f"DEBUG: data - {data}")
        data['artist_id'] = str(album.artist_id)
        print(f"DEBUG: data['artist_id'] - {data['artist_id']}")
        data['artist'] = str(album.artist)
        print(f"DEBUG: data['artist'] - {data['artist']}")
        return Response(data)
    except Album.DoesNotExist:
        return Response(
            {"error": "Album not found"},
            status=status.HTTP_404_NOT_FOUND
        )


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
    item_id_params="album_id",
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