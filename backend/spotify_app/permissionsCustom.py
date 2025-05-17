from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users based on role in the database.
    """

    def has_permission(self, request, view):
        print("Request user role:", request.role)
        # Kiểm tra role của người dùng trong cơ sở dữ liệu
        return request.role == "admin"
    
class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, view):
        return True
    
class IsAuthenticated(BasePermission):
    """
    Cho phép truy cập chỉ với người dùng đã đăng nhập.
    """

    def has_permission(self, request, view):
        print("request.user.is_authenticated:", request.user.is_authenticated)
        # Kiểm tra xem người dùng đã đăng nhập chưa
        if request.user.is_authenticated:
            return True
        return False

# Dùng để kiểm tra quyền truy cập của người dùng trong các view, hàm này gọi lại từ middleware
class AuthenticatedUserWrapper:
    def __init__(self, user, payload=None):
        self._user = user
        self._payload = payload or {}
        self._id = user._id
        self.email = user.email
        self.role = user.role

    def __getattr__(self, attr):
        return getattr(self._user, attr)

    @property
    def is_authenticated(self):
        return True



