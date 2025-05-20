import jwt
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta 
import uuid
from rest_framework.exceptions import AuthenticationFailed
from .models import User  
from bson import ObjectId  

class JWTAuthMiddleware:

    @staticmethod
    def create_access_token(user):
        access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        expiration_time = datetime.utcnow() + access_lifetime
        exp_timestamp = int(expiration_time.timestamp())
        # Tạo payload đúng chuẩn SimpleJWT
        payload = {
            "token_type": "access",
            "exp": exp_timestamp,
            "jti": str(uuid.uuid4()),  # Required for blacklist
            "user_id": str(user._id),  # SimpleJWT requires this field
            "_id": str(user._id),      # Your custom field
            "email": user.email,
            "role": str(user.role),
        }
        print("payload:", payload)
        
        access_token = jwt.encode(
            payload, 
            settings.SECRET_KEY,  # Lấy từ Django settings
            algorithm="HS256"
        )
        return access_token

    @staticmethod
    def create_refresh_token(user):
        refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        expiration_time = datetime.utcnow() + refresh_lifetime
        exp_timestamp = int(expiration_time.timestamp())
        refresh_payload = {
            "token_type": "refresh",
            "exp": exp_timestamp,
            "jti": str(uuid.uuid4()),
            "user_id": str(user._id),
            "_id": str(user._id),
            "email": user.email
        }
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        return refresh_token

    def __init__(self, get_response):
        self.get_response = get_response
        self.public_paths = [
            # swagger 
            '/api/schema',
            '/api/docs/redoc',
            '/api/docs/swagger',
            # user management
            '/user_management/register/',
            '/user_management/login/',
            '/user_management/auth/token/refresh/',
            '/admin/',
            # spotify api
            '/spotify_api/',
            # spotify app
            '/spotify_app/',
            # WebSocket
            '/ws/',
            '/payment/',

        ]

    def __call__(self, request):
        # Skip authentication for WebSocket connections
        if request.path.startswith('/ws/'):
            return self.get_response(request)
            
        if any(request.path.startswith(path) for path in self.public_paths) or request.method == 'OPTIONS':
            return self.get_response(request)
        try:
            token = request.COOKIES.get('access_token') or \
                   request.headers.get('Authorization', '').split('Bearer ')[-1]
            
            if not token:
                raise AuthenticationFailed("Token missing")

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(_id=ObjectId(payload["_id"]))  # Sử dụng _id
            print(f"User authenticated: {user}")  # In thông tin người dùng để kiểm tra
            user.role = payload.get("role")
            request.role = user.role  # Gán role cho request
            request.user = user
            request.auth = payload
            request.user.is_authenticated = True
            print("request", request)  # In thông tin người dùng
            print("request.user:", request.user)  # In thông tin người dùng trong request
            print("request.role:", request.role) 
            # Debug
            print(f"Middleware - User role: {user.role}, Type: {type(user.role)}")

        except jwt.ExpiredSignatureError:
            return JsonResponse({
                "error": "Token đã hết hạn",
                "detail": "Vui lòng đăng nhập lại"
            }, status=401)
        except (jwt.InvalidTokenError, User.DoesNotExist) as e:
            return JsonResponse({
                "error": "Token không hợp lệ",
                "detail": str(e)
            }, status=401)
        except Exception as e:
            return JsonResponse({
                "error": "Lỗi xác thực",
                "detail": str(e)
            }, status=401)

        return self.get_response(request)