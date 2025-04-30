from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # ĐANG BỊ LỖI XÁC THỰC TOKEN, NÊN TẠM THỜI BỎ QUA VIỆC YÊU CẦU TOKEN, SỬA LẠI SAU !!!!
        public_paths = [
            '/user_management/register/',
            '/user_management/login/',
            '/user_management/auth/token/refresh/',
            '/user_management/getallusers/',  # Tạm thời bỏ qua xác thực cho route này
        ]

        # Nếu là đường dẫn public hoặc OPTIONS, bỏ qua kiểm tra token
        if any(request.path.startswith(path) for path in public_paths) or request.method == 'OPTIONS':
            return self.get_response(request)

        try:
            auth = JWTAuthentication()
            validated_user = auth.authenticate(request)  # Trả về (user, token) hoặc None

            if validated_user is not None:
                request.user, request.auth = validated_user
            else:
                raise AuthenticationFailed("Token không hợp lệ hoặc không được cung cấp.")

        except AuthenticationFailed as e:
            return JsonResponse({'detail': str(e)}, status=401)
        except Exception:
            return JsonResponse({'detail': 'Lỗi xác thực token.'}, status=401)

        return self.get_response(request)
