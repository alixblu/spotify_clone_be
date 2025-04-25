from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import *

@api_view(['POST'])
def register(request):
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

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return Response({"message": "Login successful!", "data": MinimalUserSerializer(user).data}, status=200)
        else:
            return Response({"error": "Invalid credentials"}, status=401)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)