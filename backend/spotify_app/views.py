# Create your views here.
##########
from django.http import JsonResponse
import json
from datetime import datetime
from .database import db
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def custom_login(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        password = body.get("password")

        # Fetch user from database
        user = db.users.find_one({"email": email})

        if user:
            if user["password"] == password:
                # Return success along with _id, email, and role
                return JsonResponse({
                    "success": True,
                    "_id": str(user["_id"]),  # Convert ObjectId to string
                    "email": user["email"],
                    "role": user["role"],
                })
            else:
                return JsonResponse({"success": False, "error": "Invalid credentials"})
        else:
            return JsonResponse({"success": False, "error": "User not found"})
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def custom_register(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        password = body.get("password")
        name = body.get("name")
        dob = body.get("dob")
        # Check if the user already exists
        user = db.users.find_one({"email": email})
        if user:
            return JsonResponse({"success": False, "error": "User already exists"})
        
        # Add new user to database
        db.users.insert_one({"email": email, "password": password, "created_at": datetime.now()})
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request method"}, status=405)