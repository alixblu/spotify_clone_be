# Create your views here.
##########

from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from spotify_app.permissionsCustom import IsAdminUser
from .models import Song
from .serializers import SongSerializer
from mutagen.mp3 import MP3
from bson import ObjectId
from django.core.exceptions import ValidationError
import datetime
from io import BytesIO

def format_duration(seconds):
    if seconds:
        return str(datetime.timedelta(seconds=seconds))  # Converts to hh:mm:ss
    return "00:00:00"

def get_audio_duration(audio_file):
    if not audio_file:
        return None

    file_stream = BytesIO(audio_file.read())  # Convert to in-memory stream
    audio = MP3(file_stream)  # Load MP3 without saving
    return round(audio.info.length)  # Return duration in seconds

@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def upload_song(request):
    # print(f"DEBUG: Received request data - {request.data}")
    # print(f"DEBUG: Received files - {request.FILES}")

    audio_blob = request.FILES.get('audio_file')
    video_blob = request.FILES.get('video_file')

    # print(f"DEBUG: audio_file received - {audio_blob}")
    # print(f"DEBUG: video_file received - {video_blob}")

    if not audio_blob or not video_blob:
        return Response({"error": "No audio or video file received"}, status=400)

    # Process duration
    audio_duration = get_audio_duration(audio_blob) if audio_blob else None
    song_duration = format_duration(audio_duration)

    song_data = {
        'title': request.data.get('title'),
        'duration': song_duration,
        'audio_file': audio_blob,
        'video_file': video_blob,
        'img': request.data.get('img', None),
        'album_id': request.data.get('album_id', None),
    }

    serializer = SongSerializer(data=song_data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Song uploaded successfully!", "data": serializer.data}, status=201)
    
    print(f"DEBUG: Validation Errors - {serializer.errors}")
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_songs(request):
    songs = Song.objects.all()
    serializer = SongSerializer(songs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_song(request, song_id):
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        serializer = SongSerializer(song)
        return Response(serializer.data)
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)
    
from rest_framework.response import Response
from bson import ObjectId

@api_view(['PUT'])
def update_song(request, song_id):
    try:
        # Ensure song_id is a valid ObjectId
        try:
            song = Song.objects.get(_id=ObjectId(song_id))
        except (Song.DoesNotExist, ValueError):
            return Response({"error": "Invalid Song ID or Song not found"}, status=404)

        # Validate and update song data
        serializer = SongSerializer(song, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Song updated!", "data": serializer.data}, status=200)
        else:
            return Response(serializer.errors, status=400)

    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debug logs
        return Response({"error": "Internal Server Error"}, status=500)
    
@api_view(['DELETE'])
def delete_song(request, song_id):
    try:
        song = Song.objects.get(_id=ObjectId(song_id))
        song.delete()
        return Response({"message": "Song deleted successfully!"})
    except Song.DoesNotExist:
        return Response({"error": "Song not found"}, status=404)

@api_view(['PUT'])
def hide_song(request, song_id):
    try:
        # Ensure song_id is valid
        try:
            song = Song.objects.get(_id=ObjectId(song_id))
        except (Song.DoesNotExist, ValueError):
            return Response({"error": "Invalid Song ID or Song not found"}, status=404)

        # Update the song's visibility
        song.isHidden = True
        song.save()

        return Response({"message": "Song hidden successfully!", "data": {"song_id": str(song._id), "isHidden": song.isHidden}}, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")  # Debugging log
        return Response({"error": "Internal Server Error"}, status=500)

@api_view(['PUT'])
def unhide_song(request, song_id):
    try:
        # Ensure song_id is valid
        try:
            song = Song.objects.get(_id=ObjectId(song_id))
        except (Song.DoesNotExist, ValueError):
            return Response({"error": "Invalid Song ID or Song not found"}, status=404)

        # Update the song's visibility
        song.isHidden = False
        song.save()

        return Response({"message": "Song unhidden successfully!", "data": {"song_id": str(song._id), "isHidden": song.isHidden}}, status=200)

    except Exception as e:
        print(f"ERROR: {str(e)}")