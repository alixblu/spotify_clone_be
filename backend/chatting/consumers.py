import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from user_management.models import User
from bson import ObjectId

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

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
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    async def chat_message(self, event):
        # Send message to WebSocket
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