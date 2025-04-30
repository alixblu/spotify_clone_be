from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Danh sách các route public không cần xác thực
        public_paths = [
            '/user_management/login/',
            '/user_management/register/',
            '/user_management/auth/token/refresh/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Bỏ qua xác thực cho các route public và phương thức OPTIONS
        if (any(request.path.startswith(path) for path in public_paths) or 
            request.method == 'OPTIONS'):
            return self.get_response(request)
        
        # Kiểm tra token cho các route protected
        try:
            auth = JWTAuthentication()
            # Không cần gán user vào request.user
            auth.authenticate(request)  # authenticate() sẽ tự động ném ra lỗi nếu token không hợp lệ
        except AuthenticationFailed:
            return JsonResponse(
                {'detail': 'Authentication credentials were not provided or invalid.'},
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {'detail': 'Invalid or expired token.'},
                status=401
            )

        
        return self.get_response(request)



# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from django.http import JsonResponse

# class JWTAuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
    
#     def __call__(self, request):
#         # Danh sách các route public không cần xác thực
#         public_paths = [
#             '/user_management/login/',
#             '/user_management/register/',
#             '/user_management/auth/token/refresh/',
#             '/admin/',
#             '/static/',
#             '/media/',
#         ]
        
#         # Bỏ qua xác thực cho các route public và phương thức OPTIONS
#         if (any(request.path.startswith(path) for path in public_paths) or 
#             request.method == 'OPTIONS'):
#             return self.get_response(request)
        
#         # Kiểm tra token cho các route protected
#         try:
#             auth = JWTAuthentication()
#             # Không cần gán user vào request.user
#             auth.authenticate(request)  # authenticate() sẽ tự động ném ra lỗi nếu token không hợp lệ
#         except AuthenticationFailed:
#             return JsonResponse(
#                 {'detail': 'Invalid or expired token.'},
#                 status=401
#             )
#         except Exception as e:
#             # Xử lý các lỗi khác nếu có
#             return JsonResponse(
#                 {'detail': str(e)},
#                 status=500
#             )

#         return self.get_response(request)
