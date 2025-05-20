import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from user_management.models import User
from bson import ObjectId
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            
            # Get token from query string
            query_string = self.scope['query_string'].decode()
            token = None
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                    break
            
            if not token:
                print("No token provided")
                await self.close(code=4001)
                return

            # Verify token and get user
            try:
                user = await self.get_user_from_token(token)
                if not user:
                    print("Invalid token")
                    await self.close(code=4001)
                    return
                self.scope['user'] = user
            except Exception as e:
                print(f"Token verification failed: {str(e)}")
                await self.close(code=4001)
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Get current room state
            room_state = await self.get_room_state()
            
            # Notify others that a new user has joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'message': {
                        'type': 'user_joined',
                        'user_id': str(self.scope['user']._id),
                        'room_state': room_state
                    }
                }
            )
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            await self.close(code=1011)

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(_id=ObjectId(user_id))
        except Exception as e:
            print(f"Error getting user from token: {str(e)}")
            return None

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                content = text_data_json.get('message')
                user_id = text_data_json.get('user_id')
                room_id = text_data_json.get('room_id')

                # Save message to database
                message = await self.save_message(room_id, user_id, content)
                
                # Get user info
                user = await self.get_user(user_id)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            '_id': str(message._id),
                            'content': message.content,
                            'user_id': str(message.sender._id),
                            'timestamp': message.created_at.isoformat()
                        },
                        'user': {
                            '_id': str(user._id),
                            'name': user.name,
                            'profile_pic': user.profile_pic
                        }
                    }
                )
            elif message_type == 'music_control':
                try:
                    # Handle music control messages
                    message_data = text_data_json.get('message', {})
                    action = message_data.get('action')
                    song_id = message_data.get('song_id')
                    current_time = message_data.get('current_time')
                    is_playing = message_data.get('is_playing')

                    print(f"Received music control: action={action}, song_id={song_id}, current_time={current_time}, is_playing={is_playing}")

                    # Update room state in database
                    await self.update_room_state(song_id, current_time, is_playing)

                    # Get updated room state
                    room_state = await self.get_room_state()

                    # Broadcast to all users in the room
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'music_control',
                            'message': {
                                'action': action,
                                'song_id': song_id,
                                'current_time': current_time,
                                'is_playing': is_playing,
                                'room_state': room_state
                            }
                        }
                    )
                except Exception as e:
                    print(f"Error handling music control: {str(e)}")
                    # Send error back to client
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f'Error handling music control: {str(e)}'
                    }))
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            # Send error back to client
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def music_control(self, event):
        # Send music control message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        # Send user joined message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, room_id, user_id, content):
        room = ChatRoom.objects.get(_id=ObjectId(room_id))
        sender = User.objects.get(_id=ObjectId(user_id))
        message = Message.objects.create(
            room=room,
            sender=sender,
            content=content
        )
        return message

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(_id=ObjectId(user_id))

    @database_sync_to_async
    def get_room_state(self):
        room = ChatRoom.objects.get(_id=ObjectId(self.room_id))
        current_position = room.current_time
        
        if room.play_started_at and room.is_playing:
            elapsed_time = (timezone.now() - room.play_started_at).total_seconds()
            current_position = room.current_time + elapsed_time
        
        return {
            'playing_song': {
                '_id': str(room.playing_song._id),
                'title': room.playing_song.title,
                'duration': room.playing_song.duration.strftime('%M:%S'),
                'img': room.playing_song.img,
                'audio_file': room.playing_song.audio_file.url if room.playing_song.audio_file else None
            } if room.playing_song else None,
            'current_time': current_position,
            'is_playing': room.is_playing,
            'play_started_at': room.play_started_at.isoformat() if room.play_started_at else None
        }

    @database_sync_to_async
    def update_room_state(self, song_id, current_time, is_playing):
        room = ChatRoom.objects.get(_id=ObjectId(self.room_id))
        
        if song_id:
            from spotify_app.models import Song
            song = Song.objects.get(_id=ObjectId(song_id))
            room.playing_song = song
        
        if is_playing:
            # If we're starting playback, store the current time and start time
            room.current_time = current_time
            room.play_started_at = timezone.now()
            room.is_playing = True
        else:
            # If we're pausing, calculate how long the song has played
            if room.play_started_at:
                elapsed_time = (timezone.now() - room.play_started_at).total_seconds()
                room.current_time = current_time + elapsed_time
                room.play_started_at = None
                room.is_playing = False
        
        room.save() 