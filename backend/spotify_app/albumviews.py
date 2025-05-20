from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson.errors import InvalidId
from datetime import datetime
from .models import Album, Artist
from .serializers import AlbumSerializer
from backend.utils import SchemaFactory

from bson import ObjectId, errors

# 1. Create Album API
@api_view(['POST'])
@permission_classes([AllowAny])
def create_album(request):
    try:
        print("Received data:", dict(request.data), "Files:", dict(request.FILES))

        def get_string_value(field, default=''):
            value = request.data.get(field, default)
            print(f"Getting {field}:", value, type(value))
            if isinstance(value, list):
                return value[0].strip() if value and value[0] else default
            return value.strip() if isinstance(value, str) else default

        # Kiểm tra các trường bắt buộc
        required_fields = ['artist', 'album_name', 'release_date']
        for field in required_fields:
            value = get_string_value(field)
            if not value:
                return Response(
                    {"error": f"Trường '{field}' là bắt buộc."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Lấy artist_id và kiểm tra nghệ sĩ
        artist_id = get_string_value('artist')
        print("Processed artist_id:", artist_id, type(artist_id))
        try:
            artist = Artist.objects.get(_id=ObjectId(artist_id))
        except (Artist.DoesNotExist, ValueError):
            return Response(
                {"error": "ID nghệ sĩ không hợp lệ hoặc không tồn tại."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tạo dữ liệu album
        release_date = get_string_value('release_date')
        print("Processed release_date:", release_date, type(release_date))
        if not release_date:
            return Response(
                {"error": "Ngày phát hành không được để trống."},
                status=status.HTTP_400_BAD_REQUEST
            )

        album_data = {
            'artist': artist_id,  # Truyền chuỗi, serializer sẽ chuyển thành instance
            'album_name': get_string_value('album_name'),
            'artist_name': artist.artist_name,  # Lấy tên nghệ sĩ từ đối tượng Artist
            'release_date': release_date,
            'total_tracks': int(get_string_value('total_tracks', '0') or 0),
            'isfromDB': get_string_value('isfromDB', 'true').lower() == 'true',
            'isHidden': get_string_value('isHidden', 'false').lower() == 'true',
            'cover_img': get_string_value('cover_img', None),
        }

        # Debug dữ liệu trước khi serialize
        print("Album data before serializer:", album_data)

        # Lưu album
        serializer = AlbumSerializer(data=album_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Tạo album thành công!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        print("Serializer errors:", serializer.errors)
        return Response(
            {"error": "Dữ liệu không hợp lệ.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        print("Exception:", str(e))
        return Response(
            {"error": f"Lỗi hệ thống khi tạo album: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
# 2. List Albums API
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "album_name": "Album mẫu",
        "artist_name": "Nghệ sĩ XYZ",
        "cover_img": "https://example.com/cover.jpg",
        "release_date": "2023-01-01",
        "total_tracks": 10,
        "isHidden": False
    },
    search_fields=["album_name", "artist_name"],
    description="Lấy danh sách tất cả album",
    pagination=True,
    serializer=AlbumSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_albums(request):
    """ Retrieve all albums """
    try:
        albums = Album.objects.all()
        serializer = AlbumSerializer(albums, many=True)
        data = serializer.data
        
        # Convert ObjectId to string for each album
        for album in data:
            album['_id'] = str(album['_id'])
            album['artist'] = str(album['artist'])
            
        return Response(data)
    except Exception as e:
        return Response(
            {"error": f"Error retrieving albums: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 3. Get Album Detail API
@SchemaFactory.retrieve_schema(
    item_id_param="album_id",
    success_response={
        "_id": "507f1f77bcf86cd799439011",
        "album_name": "Chi tiết Album",
        "artist_name": "Nghệ sĩ ABC",
        "cover_img": "https://example.com/cover.jpg",
        "release_date": "2023-05-01",
        "total_tracks": 8,
        "isHidden": False
    },
    description="Lấy thông tin chi tiết một album"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_album(request, album_id):
    try:
        object_id = ObjectId(album_id)
    except InvalidId:
        return Response({"error": "ID album không hợp lệ."}, status=400)

    try:
        album = Album.objects.get(_id=object_id)
        serializer = AlbumSerializer(album)
        data = serializer.data
        data['_id'] = str(album._id)
        data['artist'] = str(album.artist)
        return Response(data)
    except Album.DoesNotExist:
        return Response({"error": "Không tìm thấy album."}, status=404)


# 4. Update Album API
@api_view(['POST'])
@permission_classes([AllowAny])
def create_album(request):
    try:
        print("Received data:", dict(request.data), "Files:", dict(request.FILES))

        def get_string_value(field, default=''):
            value = request.data.get(field, default)
            print(f"Getting {field}:", value, type(value))
            if isinstance(value, list):
                return value[0].strip() if value and value[0] else default
            return value.strip() if isinstance(value, str) else default

        required_fields = ['artist', 'album_name', 'release_date']
        for field in required_fields:
            value = get_string_value(field)
            if not value:
                return Response(
                    {"error": f"Trường '{field}' là bắt buộc."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        artist_id = get_string_value('artist')
        print("Processed artist_id:", artist_id, type(artist_id))

        release_date = get_string_value('release_date')
        print("Processed release_date:", release_date, type(release_date))
        if not release_date:
            return Response(
                {"error": "Ngày phát hành không được để trống."},
                status=status.HTTP_400_BAD_REQUEST
            )

        album_data = {
            'artist': artist_id,
            'album_name': get_string_value('album_name'),
            'artist_name': get_string_value('artist_name', 'Unknown Artist'),
            'release_date': release_date,
            'total_tracks': int(get_string_value('total_tracks', '0') or 0),
            'isfromDB': get_string_value('isfromDB', 'true').lower() == 'true',
            'isHidden': get_string_value('isHidden', 'false').lower() == 'true',
            'cover_img': get_string_value('cover_img', None),
        }

        print("Album data before serializer:", album_data)

        serializer = AlbumSerializer(data=album_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Tạo album thành công!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        print("Serializer errors:", serializer.errors)
        return Response(
            {"error": "Dữ liệu không hợp lệ.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        print("Exception:", str(e))
        return Response(
            {"error": f"Lỗi hệ thống khi tạo album: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_album(request, albumId):
    try:
        print("Received data:", dict(request.data), "Files:", dict(request.FILES))

        # Lấy album hiện có
        try:
            album = Album.objects.get(_id=ObjectId(albumId))
        except (Album.DoesNotExist, ValueError):
            return Response(
                {"error": "Album không tồn tại hoặc ID không hợp lệ."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Hàm lấy chuỗi từ request.data
        def get_string_value(field, default=''):
            value = request.data.get(field, default)
            print(f"Getting {field}:", value, type(value))
            if isinstance(value, list):
                return value[0].strip() if value and value[0] else default
            return value.strip() if isinstance(value, str) else default

        # Kiểm tra các trường bắt buộc
        required_fields = ['artist', 'album_name', 'release_date']
        for field in required_fields:
            value = get_string_value(field)
            if not value:
                return Response(
                    {"error": f"Trường '{field}' là bắt buộc."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Lấy artist_id
        artist_id = get_string_value('artist')
        print("Processed artist_id:", artist_id, type(artist_id))

        # Tạo dữ liệu album
        release_date = get_string_value('release_date')
        print("Processed release_date:", release_date, type(release_date))
        if not release_date:
            return Response(
                {"error": "Ngày phát hành không được để trống."},
                status=status.HTTP_400_BAD_REQUEST
            )

        album_data = {
            'artist': artist_id,
            'album_name': get_string_value('album_name'),
            'artist_name': get_string_value('artist_name', album.artist_name),
            'release_date': release_date,
            'total_tracks': int(get_string_value('total_tracks', '0') or 0),
            'isfromDB': get_string_value('isfromDB', 'true').lower() == 'true',
            'isHidden': get_string_value('isHidden', 'false').lower() == 'true',
            'cover_img': get_string_value('cover_img', None),
        }

        # Debug dữ liệu trước khi serialize
        print("Album data before serializer:", album_data)

        # Cập nhật album
        serializer = AlbumSerializer(album, data=album_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Cập nhật album thành công!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        print("Serializer errors:", serializer.errors)
        return Response(
            {"error": "Dữ liệu không hợp lệ.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        print("Exception:", str(e))
        return Response(
            {"error": f"Lỗi hệ thống khi cập nhật album: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 5. Delete Album API
@SchemaFactory.delete_schema(
    item_id_params="album_id",
    success_response={"message": "Album đã bị xóa!"},
    description="Xóa album"
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_album(request, album_id):
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        album.delete()
        return Response({"message": "Album đã bị xóa!"})
    except (Album.DoesNotExist, InvalidId):
        return Response({"error": "Không tìm thấy album."}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_albums_by_artist(request, artist_id):
    try:
        artist = Artist.objects.get(_id=ObjectId(artist_id))
        albums = Album.objects.filter(artist=artist)
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)
    except (Artist.DoesNotExist, InvalidId):
        return Response({"error": "Không tìm thấy nghệ sĩ."}, status=404)