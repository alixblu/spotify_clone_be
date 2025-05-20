from datetime import datetime, timedelta
from user_management.models import User
def update_user(user_email, **kwargs):
    try:
        user = User.objects.get(email=user_email)
        for key, value in kwargs.items():
            setattr(user, key, value)  # Dynamically update fields
        user.save()
        return {"success": True, "updated_user": {
            "name": user.name,
            "email": user.email,
        }}
    except User.DoesNotExist:
        return {"success": False, "error": "User not found"}
    
def delete_user(user_email):
    try:
        user = User.objects.get(email=user_email)
        user.delete()
        return {"success": True}
    except User.DoesNotExist:
        return {"success": False, "error": "User not found"}

def activate_premium(user_email):
    try:
        user = User.objects.get(email=user_email)
        if(user.premium_expired_at is None or not hasattr(user, 'premium_expired_at')):
            user.premium_expired_at = datetime.now() + timedelta(years=1)
        else:
            return {
                "success": False, "message": "Premium trail already activated"
            }
        user.save()
        return {"success": True}
    except User.DoesNotExist:
        return {"success": False, "error": "User not found"}