from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .models import User
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from bson import ObjectId
import traceback

@api_view(['POST'])
# @permission_classes([AllowAny])  # Không yêu cầu token
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

    
@api_view(['POST'])
# @permission_classes([AllowAny])  # Không yêu cầu token
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            # Tạo token thủ công
            # # refresh = RefreshToken()
            # # user_id = str(user._id) if isinstance(user._id, ObjectId) else str(user._id)
            user_id = str(user._id)
            refresh = RefreshToken()
            refresh['_id'] = user_id  # Claim phải khớp với SIMPLE_JWT config
            refresh['token_type'] = 'refresh'  # Thêm token_type bắt buộc
            access = refresh.access_token
            access['_id'] = user_id
            access['token_type'] = 'access'    # Thêm token_type bắt buộc

            # # Đảm bảo user._id là string
            # user_id = str(user._id) if isinstance(user._id, ObjectId) else user._id

            # # Tạo token thủ công với payload chuẩn
            # refresh = RefreshToken()
            # refresh['user_id'] = user_id 
            # refresh['token_type'] = 'refresh'

            # access = refresh.access_token
            # access['user_id'] = user_id
            # access['token_type'] = 'access'
            # ĐẢM BẢO DÙNG ĐÚNG _id TỪ DATABASE

            # Tạo token thủ công (không dùng for_user)
          
            # refresh = RefreshToken()
            # refresh['_id'] = str(user._id)  # Convert ObjectId -> string
            # refresh['token_type'] = 'refresh'
            
            # access = refresh.access_token
            # access['_id'] = str(user._id)
     
            # Tạo response
            response = Response({
                "success": True,
                "message": "Login successful!",
                "user": MinimalUserSerializer(user).data,
                "access_token": str(access),
                "refresh_token": str(refresh),
            })
            # Set HttpOnly Cookie cho refresh token (chỉ backend truy cập được)
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,  # Chống XSS
                secure=False,     # Chỉ gửi qua HTTPS
                samesite="Lax",
                max_age=timedelta(days=7).total_seconds(),  # 7 ngày
                # path="/auth/",  # Chỉ gửi cookie tới các route /auth/*
                )

            return response
            # return Response({"message": "Login successful!", "data": MinimalUserSerializer(user).data}, status=200)
        else:
            return Response({"success": False, "error": "Incorrect email or password"}, status=401)
    except User.DoesNotExist:
        return Response({"success": False, "error": "Incorrect email or password"}, status=404)
    
# API refresh access token  
@api_view(['POST'])
# @permission_classes([AllowAny])  # Không yêu cầu token
def refresh_access_token(request):
    # 1. Lấy refresh token từ cookie
    refresh_token = request.COOKIES.get('refresh_token')
    
    # 2. Kiểm tra nếu không có token
    if not refresh_token:
        return Response({"error": "No refresh token provided."}, status=401)

    try:
        # 3. Xác thực refresh token
        refresh = RefreshToken(refresh_token)
        
        # 4. Lấy user ID từ token
        user_id = refresh['_id']

        # 5. Tạo access token mới từ refresh token
        access = refresh.access_token
        
        # 6. Thêm user ID vào access token
        access['_id'] = user_id

        # 7. Tạo response chứa access token mới
        response = Response({
            "message": "Access token refreshed successfully",
            "access_token": str(access)
        })

        return response

    except Exception as e:
        # 8. Xử lý lỗi nếu token không hợp lệ
        return Response({"error": "Invalid or expired refresh token."}, status=401)

@api_view(['GET'])
def get_user_list(request):
    # Lấy tất cả người dùng từ cơ sở dữ liệu
    users = User.objects.all()
    
    # Serialize dữ liệu
    serialized_users = UserSerializer(users, many=True)
    
    # Trả về danh sách người dùng
    return Response({"message": "User list retrieved successfully", "data": serialized_users.data}, status=200)