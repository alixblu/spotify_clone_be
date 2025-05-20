from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import *
from datetime import timedelta
from django.conf import settings
import traceback
import jwt
from spotify_app.middlewares import JWTAuthMiddleware
from spotify_app.permissionsCustom import IsAdminUser
from rest_framework.pagination import LimitOffsetPagination
from backend.utils import SchemaFactory

from bson import ObjectId  # Import this at the top


# 1. Register API
@SchemaFactory.post_schema(
    request_example={
        "name": "Nguyễn Văn A",
        "dob": "1990-01-01",
        "gender": "male",
        "email": "user@example.com",
        "password": "Password@123"
    },
    success_response={
        "message": "User registered successfully!",
        "data": {
            "_id": "681516ff88db30c4bebe9018",
            "role": "user"
        }
    },
    error_responses=[
        {
            "name": "Email tồn tại",
            "response": {"error": "Email đã được sử dụng"},
            "status_code": 400
        }
    ],
    description="Đăng ký tài khoản mới",
    request_serializer=UserSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        required_fields = ['name', 'dob', 'gender', 'email', 'password']
        if not all(field in request.data for field in required_fields):
            return Response({"error": "Missing required fields"}, status=400)

        if User.objects.filter(email=request.data['email']).exists():
            return Response({"error": "Email already registered"}, status=400)

        role = request.data.get('role', 'user') 

        user = User.objects.create(
            name=request.data['name'],
            dob=request.data['dob'],
            gender=request.data['gender'],
            email=request.data['email'],
            password=request.data['password'],
            role=role,
        )

        return Response({
            "message": "User registered successfully!",
            "data": MinimalUserSerializer(user).data
        }, status=201)

    except Exception as e:
        traceback.print_exc()
        return Response({
            "error": "Registration failed",
            "detail": str(e)
        }, status=500)


# 2. Login API
@SchemaFactory.post_schema(
    request_example={
        "email": "test2@example.com",
        "password": "SecurePassword123"
    },
    success_response={
        "success": True,
        "message": "Đăng nhập thành công",
        "data": {
            "_id": "681328a710b9a4734a894e64",
            "role": "admin"
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2MjExNTk3LCJqdGkiOiJjNGNlZGFlMS1lYzM3LTQ4M2EtOGIxYS0yYjNlN2ViYTk0OGYiLCJ1c2VyX2lkIjoiNjgxMzI4YTcxMGI5YTQ3MzRhODk0ZTY0IiwiX2lkIjoiNjgxMzI4YTcxMGI5YTQ3MzRhODk0ZTY0IiwiZW1haWwiOiJ0ZXN0MkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiJ9.fZKSXR9MYOnZQeB1c5h9Y-EztWZgy0TSpJ0tMG7loSM",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NjgxMzM5NywianRpIjoiMWRmNjliYmItZmYwZi00M2ZhLTkzMWUtM2IxMDQxMGRmYzQ0IiwidXNlcl9pZCI6IjY4MTMyOGE3MTBiOWE0NzM0YTg5NGU2NCIsIl9pZCI6IjY4MTMyOGE3MTBiOWE0NzM0YTg5NGU2NCIsImVtYWlsIjoidGVzdDJAZXhhbXBsZS5jb20ifQ.74s5zdxCWYHy6iPZAupcI8B0hnfJLW-Fd0aG1oYF0ic"
    },
    error_responses=[
        {
            "name": "Sai thông tin đăng nhập",
            "response": {"error": "Email hoặc mật khẩu không đúng"},
            "status_code": 401
        }
    ],
    description="Đăng nhập hệ thống",
    request_serializer=MinimalUserSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Lấy email và password từ request
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Validate input
    if not email or not password:
        return Response({
            "success": False,
            "error": "Email và mật khẩu là bắt buộc"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Tìm user bằng email
        user = User.objects.get(email=email)
        
        # Kiểm tra mật khẩu
        if not user.check_password(password):
            return Response({
                "success": False,
                "error": "Email hoặc mật khẩu không đúng"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Tạo access_token
        access_token = JWTAuthMiddleware.create_access_token(user)
        # Tạo refresh_token thủ công
        refresh_token = JWTAuthMiddleware.create_refresh_token(user)
        # Tạo response
        response_data = {
            "success": True,
            "message": "Đăng nhập thành công",
            # "data": MinimalUserSerializer(user).data,
            "_id": str(user.id),
            "role": user.role,
            "access_token": access_token,  # Trả token trong response
            "refresh_token": refresh_token
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        # Set HttpOnly Cookie cho refresh token (chỉ backend truy cập được)
        # Gửi refresh token dưới dạng HttpOnly Cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=int(timedelta(days=7).total_seconds())
        )

        return response

    except User.DoesNotExist:
        return Response({
            "success": False,
            "error": "Email hoặc mật khẩu không đúng"
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            "success": False,
            "error": "Đã xảy ra lỗi khi đăng nhập",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 3. Refresh Token API
@SchemaFactory.post_schema(
    success_response={
        "message": "Làm mới token thành công",
        "access_token": "eyJhbGci...",
        "data": {
            "_id": "507f1f77bcf86cd799439011",
            "role": "admin"
        }
    },
    error_responses=[
        {
            "name": "Token không hợp lệ",
            "response": {"error": "Refresh token không hợp lệ hoặc đã hết hạn"},
            "status_code": 401
        }
    ],
    description="Làm mới access token bằng refresh token"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request):
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response({"error": "Không tìm thấy refresh token."}, status=401)

    try:
        decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        
        if decoded.get("token_type") != "refresh":
            return Response({"error": "Token không hợp lệ."}, status=401)

        email = decoded.get("email")
         # Tìm user bằng email
        user = User.objects.get(email=email)
        
        # Tạo access_token
        new_access_token = JWTAuthMiddleware.create_access_token(user)
        return Response({
            "message": "Cấp lại access token thành công",
            "data": MinimalUserSerializer(user).data,
            "access_token": new_access_token
        })

    except jwt.ExpiredSignatureError:
        return Response({"error": "Refresh token đã hết hạn."}, status=401)

    except jwt.InvalidTokenError:
        return Response({"error": "Refresh token không hợp lệ."}, status=401)

    except Exception as e:
        return Response({"error": "Đã xảy ra lỗi.", "detail": str(e)}, status=500)


# 4. Get Users List API
@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "name": "Nguyễn Văn A",
        "email": "user@example.com",
        "role": "user"
    },
    search_fields=["email", "name"],
    description="Lấy danh sách người dùng (yêu cầu quyền admin)",
    pagination=True,
    serializer=UserSerializer
)
@api_view(['GET'])
# @permission_classes([IsAdminUser])
@permission_classes([AllowAny])
# @permission_classes([IsAuthenticated])
def get_user_list(request):
    # Lọc theo email và name
    email = request.query_params.get('email')
    name = request.query_params.get('name')

    queryset = User.objects.all()
    if email:
        queryset = queryset.filter(email__icontains=email)
    if name:
        queryset = queryset.filter(name__icontains=name)  # hoặc 'name' nếu model có field đó

    # Phân trang
    paginator = LimitOffsetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request, view=None)
    serializer = UserSerializer(paginated_queryset, many=True)

    # Trả về response phân trang
    return paginator.get_paginated_response({
        "success": True,
        "message": "User list retrieved successfully",
        "data": serializer.data
    })





@SchemaFactory.update_schema(
    item_id_param="_id",  # Thêm tham số _id trong URL
    request_example={
        "name": "Nguyễn Văn B",
        "dob": "1992-05-15",
        "gender": "female",
        "password": "NewPassword@123",
        "profile_pic": "https://example.com/profile-images/user123.jpg"
    },
    success_response={
        "success": True,
        "message": "Cập nhật thông tin người dùng thành công",
        "data": {
            "_id": "681516ff88db30c4bebe9018",
            "name": "Nguyễn Văn B",
            "email": "user@example.com",
            "dob": "1992-05-15",
            "gender": "female",
            "profile_pic": "https://example.com/profile-images/user123.jpg",
            "role": "user"
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy người dùng",
            "response": {"error": "Không tìm thấy người dùng"},
            "status_code": 404
        },
        {
            "name": "Lỗi xác thực",
            "response": {"error": "Bạn không có quyền cập nhật thông tin người dùng này"},
            "status_code": 403
        },
        {
            "name": "Lỗi server",
            "response": {"error": "Đã xảy ra lỗi khi cập nhật thông tin người dùng"},
            "status_code": 500
        }
    ],
    description="Cập nhật thông tin người dùng (name, dob, gender, password, profile_pic)",
    request_serializer=UserSerializer
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user(request, _id=None):
    print(f"Received request for user_id: {_id}")  # Debugging line
    try:
        # Use _id field in the query for MongoDB (Djongo)
        try:
            user = User.objects.get(_id=ObjectId(_id))# Searching by _id, not id
            print(f"User found: {user}")
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "Không tìm thấy người dùng"
            }, status=status.HTTP_404_NOT_FOUND)

        # Update user fields as needed
        allowed_fields = ['name', 'dob', 'gender', 'profile_pic']
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])

        if 'password' in request.data and request.data['password']:
            new_password = request.data['password']  # Mật khẩu mới từ yêu cầu
            user.password = new_password  # Cập nhật mật khẩu

        user.save()

        return Response({
            "success": True,
            "message": "Cập nhật thông tin người dùng thành công",
            "data": UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        traceback.print_exc()
        return Response({
            "success": False,
            "error": "Đã xảy ra lỗi khi cập nhật thông tin người dùng",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "name": "Nguyễn Văn A",
        "email": "user@example.com",
        "role": "user"
    },
    description="Lấy thông tin chi tiết người dùng bằng _id",
    pagination=False,  # Tắt phân trang vì đây là API get single item
    search_fields=None  # Không cần search fields
)
@api_view(['GET'])
@permission_classes([AllowAny])  # Only authenticated users can access
def get_user_by_id(request , _id=None):
    try:
        # Use _id field to query the MongoDB database
        user = User.objects.get(_id=ObjectId(_id))
        
        # Return the user data using the serializer
        return Response({
            "success": True,
            "message": "User information retrieved successfully",
            "data": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({
            "success": False,
            "error": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        traceback.print_exc()
        return Response({
            "success": False,
            "error": "An error occurred while retrieving user information",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([AllowAny])  # Hoặc IsAuthenticated nếu có xác thực
def update_user_is_hidden(request, _id=None):
    try:
        user = User.objects.get(_id=ObjectId(_id))
    except User.DoesNotExist:
        return Response({"success": False, "error": "User not found"}, status=404)

    # ❌ Không cho phép ẩn tài khoản admin
    if user.role == "admin":
        return Response({
            "success": False,
            "error": "Không thể thay đổi trạng thái ẩn của tài khoản admin"
        }, status=403)

    is_hidden = request.data.get('isHidden')

    if not isinstance(is_hidden, bool):
        return Response({
            "success": False,
            "error": "isHidden phải là kiểu boolean"
        }, status=400)

    user.isHidden = is_hidden
    user.save()

    return Response({
        "success": True,
        "message": f"isHidden updated to {is_hidden}",
        "data": {"_id": str(user._id), "isHidden": user.isHidden}
    }, status=200)
