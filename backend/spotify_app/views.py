# Create your views here.
##########
from django.http import JsonResponse
import json
from datetime import datetime
from .database import db
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Song
from .serializers import SongSerializer

@api_view(['POST'])
def create_song(request, parser_classes=[MultiPartParser, FormParser]):
    audio_blob = request.FILES.get('audio_file').read() if 'audio_file' in request.FILES else None
    video_blob = request.FILES.get('video_file').read() if 'video_file' in request.FILES else None
    
    song_data = {
        'title': request.data.get('title'),
        'duration': request.data.get('duration'),
        'audio_file': audio_blob,
        'video_file': video_blob,
        'img': request.data.get('img'),
        'album_id': request.data.get('album_id'),
        'isfromDB': True,
    }

    serializer = SongSerializer(data=song_data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Song uploaded successfully!", "data": serializer.data}, status=201)
    
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def list_songs(request):
    songs = Song.objects.all()
    serializer = SongSerializer(songs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_song(request, song_id):
    try:
        song = Song.objects.get(_id=song_id)
        serializer = SongSerializer(song)
        return Response(serializer.data)
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    
@api_view(['PUT'])
def update_song(request, song_id):
    try:
        song = Song.objects.get(_id=song_id)
        serializer = SongSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Song updated!", "data": serializer.data})
        return Response(serializer.errors, status=400)
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    
@api_view(['DELETE'])
def delete_song(request, song_id):
    try:
        song = Song.objects.get(_id=song_id)
        song.delete()
        return Response({"message": "Song deleted successfully!"})
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    

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