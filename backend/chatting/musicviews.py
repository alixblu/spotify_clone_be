from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatRoom
from spotify_app.models import Song

@api_view(['GET'])
@permission_classes([AllowAny])
def get_room_playlist(request, room_id):
    """Get the playlist for a room"""
    try:
        room = get_object_or_404(ChatRoom, _id=ObjectId(room_id))
        if not room.song_list:
            return Response({
                'songs': [],
                'message': 'No songs in this room'
            })
        
        # Get all songs in the song list
        songs = room.song_list.all()
        song_list = [{
            'id': str(song._id),
            'title': song.title,
            'duration': song.duration.strftime('%M:%S'),
            'img': song.img,
            'audio_file': song.audio_file.url if song.audio_file else None
        } for song in songs]
        
        return Response({
            'songs': song_list
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_song_to_room_playlist(request, room_id):
    """Add a song to the room's song list"""
    try:
        room = get_object_or_404(ChatRoom, _id=ObjectId(room_id))
        song_id = request.data.get('song_id')
        
        if not song_id:
            return Response({'error': 'Song ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        song = get_object_or_404(Song, _id=ObjectId(song_id))
        
        # Add song to song list if not already present
        if song not in room.song_list.all():
            room.song_list.add(song)
            
            # Notify all users in the room about the new song
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{room_id}",
                {
                    'type': 'playlist_update',
                    'message': {
                        'type': 'add_song',
                        'song': {
                            'id': str(song._id),
                            'title': song.title,
                            'duration': song.duration.strftime('%M:%S'),
                            'img': song.img,
                            'audio_file': song.audio_file.url if song.audio_file else None
                        }
                    }
                }
            )
        
        return Response({'message': 'Song added to playlist'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def remove_song_from_room_playlist(request, room_id):
    """Remove a song from the room's song list"""
    try:
        room = get_object_or_404(ChatRoom, _id=ObjectId(room_id))
        song_id = request.data.get('song_id')
        
        if not song_id:
            return Response({'error': 'Song ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not room.song_list:
            return Response({'error': 'Room has no songs'}, status=status.HTTP_400_BAD_REQUEST)
        
        song = get_object_or_404(Song, _id=ObjectId(song_id))
        
        # Remove song from song list
        room.song_list.remove(song)
        
        # Notify all users in the room about the removed song
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}",
            {
                'type': 'playlist_update',
                'message': {
                    'type': 'remove_song',
                    'song_id': str(song._id)
                }
            }
        )
        
        return Response({'message': 'Song removed from playlist'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 