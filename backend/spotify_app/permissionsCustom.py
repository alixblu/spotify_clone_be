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
