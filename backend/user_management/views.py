from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import *
from datetime import datetime, timedelta
from django.conf import settings
import traceback
import jwt
import uuid
from spotify_app.middlewares import JWTAuthMiddleware
from spotify_app.permissionsCustom import IsAdminUser
from rest_framework.pagination import LimitOffsetPagination

@api_view(['POST'])
@permission_classes([AllowAny])  # Cho phép bất kỳ ai truy cập
def register(request):
    try:
        required_fields = ['name', 'dob', 'gender', 'email', 'password']
        if not all(field in request.data for field in required_fields):
            return Response({"error": "Missing required fields"}, status=400)

        if User.objects.filter(email=request.data['email']).exists():
            return Response({"error": "Email already registered"}, status=400)

        user = User.objects.create(
            name=request.data['name'],
            dob=request.data['dob'],
            gender=request.data['gender'],
            email=request.data['email'],
            password=request.data['password'],  # Auto-hashed in the model
            role='user',
        )

        return Response({"message": "User registered successfully!", "data": MinimalUserSerializer(user).data}, status=201)
    except Exception as e:
        traceback.print_exc()
        return Response({
            "error": "Registration failed",
            "detail": str(e)
        }, status=500)

# API đăng nhập
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
            "data": MinimalUserSerializer(user).data,
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


# API refresh access token  
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


# API lấy danh sách người dùng
@api_view(['GET'])
@permission_classes([IsAdminUser])
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