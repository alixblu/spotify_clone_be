from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaylistSerializer
from bson import ObjectId
from user_management.models import User
from spotify_app.permissionsCustom import IsAdminUser

# API để tạo playlist mới
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
