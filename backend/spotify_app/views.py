# Create your views here.
##########

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Song
from .serializers import SongSerializer
from mutagen.mp3 import MP3
from django.core.files.storage import default_storage

import os
import datetime

def format_duration(seconds):
    if seconds:
        return str(datetime.timedelta(seconds=seconds))  # Converts to hh:mm:ss
    return "00:00:00"


def get_audio_duration(audio_file):
    if not audio_file:
        return None
    
    temp_filename = "temp_audio.mp3"  # Explicit filename
    temp_file_path = os.path.join(default_storage.location, temp_filename)

    # Save file correctly before trying to read it
    with default_storage.open(temp_filename, 'wb') as temp_file:
        temp_file.write(audio_file.read())

    audio = MP3(temp_file_path)  # Load file correctly now that it exists
    return round(audio.info.length)  # Return duration in seconds safely


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_song(request):
    audio_blob = request.FILES.get('audio_file')
    video_blob = request.FILES.get('video_file')

    audio_duration = get_audio_duration(audio_blob) if audio_blob else None
    # video_duration = get_video_duration(video_blob) if video_blob else None
    song_duration = format_duration(audio_duration)

    song_data = {
        'title': request.data.get('title'),
        'duration': song_duration,  # Automatically filled
        'audio_file': audio_blob.read() if audio_blob else None,
        'video_file': video_blob.read() if video_blob else None,
        'img': request.data.get('img', None),
        'album_id': request.data.get('album_id', None),
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
    

