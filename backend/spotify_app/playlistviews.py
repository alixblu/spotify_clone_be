from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaylistSerializer
from bson import ObjectId
from bson.errors import InvalidId
from user_management.models import User
from spotify_app.models import Playlist
from spotify_app.permissionsCustom import IsAdminUser, IsAuthenticated
from backend.utils import SchemaFactory

# API để tạo playlist mới
@SchemaFactory.post_schema(
    request_example={
        "user_id": "681328a710b9a4734a894e64",
        "name": "test playlist 3",
        "cover_img": "https://example.com/cover.jpg",
        "isfromDB": True,
        "isHidden": False
    },
    success_response={
        "message": "Playlist created successfully",
        "playlist": {
            "_id": "681531042ef7b7aa4f06830d",
            "name": "test playlist 3",
            "cover_img": "https://example.com/cover.jpg",
            "created_at": "2025-05-02T20:54:28.043902Z",
            "isfromDB": True,
            "isHidden": False,
            "user_id": "681328a710b9a4734a894e64"
        }
    },
    error_responses=[
        {
            "name": "Thiếu user_id",
            "response": {"error": "User ID is required"},
            "status_code": 400
        },
        {
            "name": "User không tồn tại",
            "response": {"error": "This field is required."},
            "status_code": 404
        }
    ],
    description="Tạo playlist mới cho người dùng",
    request_serializer=PlaylistSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_playlist(request):
    # Nhận dữ liệu từ yêu cầu POST
    user_id = request.data.get('user_id')
    print(f"DEBUG: Received user_id - {user_id}")
    # Kiểm tra nếu user_id được cung cấp
    if not user_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Chuyển user_id thành ObjectId
    try:
        user_id = ObjectId(user_id)  # Chuyển chuỗi thành ObjectId
        print(f"DEBUG: Converted user_id to ObjectId - {user_id}")
    except Exception as e:
        return Response({"error": f"Invalid user_id format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra sự tồn tại của người dùng trong cơ sở dữ liệu
    try:
        user = User.objects.get(_id=user_id)
        print(f"DEBUG: User found - {user}")
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    print("user_id", user_id)  # In thông tin người dùng để kiểm tra
    # Thêm user_id vào dữ liệu request trước khi serializer lưu
    request.data['user_id'] = user_id  # Gán user_id đã chuyển thành ObjectId

    # Khởi tạo serializer với dữ liệu đã chỉnh sửa
    serializer = PlaylistSerializer(data=request.data)

    # Kiểm tra tính hợp lệ của dữ liệu
    if serializer.is_valid():
        playlist = serializer.save()  # Lưu playlist vào cơ sở dữ liệu
        print(f"Playlist created: {playlist}")
        # Chuyển ObjectId thành chuỗi trước khi trả về
        playlist_data = serializer.data
        playlist_data['user_id'] = str(playlist_data['user_id'])  # Chuyển ObjectId thành string

        # Trả về response nếu tạo playlist thành công
        return Response({
            "message": "Playlist created successfully",
            "playlist": playlist_data  # Trả về dữ liệu của playlist vừa tạo
        }, status=status.HTTP_201_CREATED)
    
    # Trả về lỗi nếu dữ liệu không hợp lệ
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# API để lấy danh sách playlist theo id
@SchemaFactory.list_schema(
        item_example={
            "id": "string",
            "title": "My Playlist",
            "description": "A great playlist",
            # các field khác...
        },
        search_fields=None,
        pagination=False,
        description="Lấy thông tin chi tiết của một playlist",
        serializer=PlaylistSerializer
    )
@api_view(['GET'])
@permission_classes([AllowAny])
def get_playlist_by_id(request, playlist_id):
    try:
        # Kiểm tra playlist_id có phải là ObjectId hợp lệ không
        object_id = ObjectId(playlist_id)
    except (InvalidId, TypeError, ValueError):
        return Response({
            "success": False,
            "message": "Invalid playlist ID format"
        }, status=400)

    try:
        playlist = Playlist.objects.get(_id=object_id)
        serializer = PlaylistSerializer(playlist)
        playlist_data = serializer.data
        # Ép kiểu các ObjectId về string
        playlist_data['_id'] = str(playlist._id)
        playlist_data['user_id'] = str(playlist.user_id)

        return Response({
            "success": True,
            "message": "Playlist retrieved successfully",
            "data": playlist_data
        }, status=200)
    except Playlist.DoesNotExist:
        return Response({
            "success": False,
            "message": "Playlist not found"
        }, status=404)
    except Exception as e:
        # Ghi log nếu cần
        return Response({
            "success": False,
            "message": "An unexpected error occurred",
            "detail": str(e)  # Có thể bỏ chi tiết lỗi ở production
        }, status=500)
    

# API để lấy danh sách tất cả playlist của user_id
@SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "_id": "string",
        "title": "My Playlist",
        "description": "A great playlist",
        "user_id": "string"
    },
    error_responses=[
        {
            "name": "Invalid ID",
            "response": {"error": "Invalid user ID format"},
            "status_code": 400
        },
        {
            "name": "Not Found",
            "response": {"error": "User not found"},
            "status_code": 404
        }
    ],
    description="Lấy danh sách tất cả playlist của người dùng theo user_id",
    serializer=PlaylistSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_alls_playlists_by_user(request, user_id):
    try:
        # Validate user_id
        if not ObjectId.is_valid(user_id):
            return Response({"error": "Invalid user ID format"}, status=400)

        user_obj_id = ObjectId(user_id)

        # Check if user exists
        if not User.objects.filter(_id=user_obj_id).exists():
            return Response({"error": "User not found"}, status=404)

        # Get playlists with manual serialization
        playlists = Playlist.objects.filter(user_id=user_obj_id)
        
        # Manually serialize each playlist
        playlists_data = []
        for playlist in playlists:
            playlists_data.append({
                '_id': str(playlist._id),
                'title': playlist.name,
                'description': len(playlists_data),
                'image': playlist.cover_img,
                'user_id': str(playlist.user_id),
                
            })

        return Response({
            "success": True,
            "count": len(playlists_data),
            "data": playlists_data
        })

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)
    

# API để cập nhật thông tin playlist
@SchemaFactory.update_schema(
    item_id_param="playlist_id",
    request_example={
        "name": "Tên Playlist mới",
        "img": "https://example.com/new_image.jpg"
    },
    success_response={
        "message": "Playlist updated!",
        "data": {
            "_id": "507f1f77bcf86cd799439011",
            "user_id": "681328a710b9a4734a894e64",
            "name": "Tên Playlist mới",
            "cover_img": "https://example.com/new_image.jpg",
            "created_at": "2025-05-02T20:54:28.043902Z",
            "isfromDB": True,
            "isHidden": False,
        }
    },
    error_responses=None,
    description="Update song information (partial update supported)",
    request_serializer=PlaylistSerializer,
    
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_playlist(request, playlist_id):
    try:
        # Lấy playlist từ database
        playlist = Playlist.objects.get(_id=ObjectId(playlist_id))
        
        # Kiểm tra quyền truy cập (chỉ cho phép người tạo playlist hoặc admin)
        if str(playlist.user_id) != str(request.user.id) and not request.user.is_staff:
            return Response({"error": "Unauthorized!!!, Only allow playlist creator or admin"}, status=403)
        
        # Cập nhật playlist với dữ liệu request
        serializer = PlaylistSerializer(playlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    except Playlist.DoesNotExist:
        return Response({"error": "Playlist not found"}, status=404)
    

# API để xóa playlist
@SchemaFactory.delete_schema(
    item_id_params="playlist_id",
    success_response={"message": "Playlist deleted successfully"},
    error_responses=[
        {
            "status_code": 403,
            "description": "Unauthorized",
            "response": {"error": "Unauthorized"}
        },
        {
            "status_code": 404,
            "description": "Playlist not found",
            "response": {"error": "Playlist not found"}
        }
    ],
    description="Delete a playlist by ID"
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_playlist(request, playlist_id):
    try:
        playlist = Playlist.objects.get(_id=ObjectId(playlist_id))
        if playlist.user_id != request.user.id and not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=403)

        playlist.delete()
        return Response({"message": "Playlist deleted successfully"}, status=204)
    except Playlist.DoesNotExist:
        return Response({"error": "Playlist not found"}, status=404)
