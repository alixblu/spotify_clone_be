from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from rest_framework.pagination import LimitOffsetPagination
from backend.utils import SchemaFactory
from .models import ChatRoom, Message
from user_management.models import User
from django.utils import timezone

@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "content": "Hello everyone!",
        "sender": "507f1f77bcf86cd799439012",
        "created_at": "2025-05-18T08:30:00Z"
    },
    description="Get all messages in a chat room",
    pagination=True
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_messages(request, room_id):
    try:
        # Verify room exists
        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get messages for the room, ordered by created_at
        messages = Message.objects.filter(room=room).order_by('created_at')
        
        # Apply pagination
        paginator = LimitOffsetPagination()
        paginated_messages = paginator.paginate_queryset(messages, request)
        
        # Format response with user information
        message_list = []
        for msg in paginated_messages:
            try:
                user = User.objects.get(_id=msg.sender._id)
                message_list.append({
                    "_id": str(msg._id),
                    "content": msg.content,
                    "user_id": str(msg.sender._id),
                    "timestamp": msg.created_at.isoformat(),
                    "user": {
                        "_id": str(user._id),
                        "name": user.name,
                        "profile_pic": user.profile_pic
                    }
                })
            except User.DoesNotExist:
                # Skip messages from deleted users
                continue

        return Response({
            "count": len(message_list),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": message_list
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.post_schema(
    request_example={
        "content": "Hello everyone!"
    },
    success_response={
        "message": "Message sent successfully",
        "message_id": "507f1f77bcf86cd799439011"
    },
    error_responses=[
        {
            "name": "Room Not Found",
            "response": {"error": "Room not found"},
            "status_code": 404
        },
        {
            "name": "Invalid Content",
            "response": {"error": "Message content is required"},
            "status_code": 400
        },
        {
            "name": "User Not Found",
            "response": {"error": "User not found"},
            "status_code": 404
        },
        {
            "name": "User Not in Room",
            "response": {"error": "You must be a member of the room to send messages"},
            "status_code": 403
        }
    ],
    description="Send a new message to a chat room"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request, room_id):
    try:
        content = request.data.get('content')
        if not content:
            return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify room exists
        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get sender from request (assuming it's set by authentication middleware)
        sender_id = request.user._id if hasattr(request, 'user') else None
        if not sender_id:
            return Response({"error": "Sender not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify sender exists and is a member of the room
        try:
            sender = User.objects.get(_id=sender_id)
            if sender not in room.users.all():
                return Response({"error": "You must be a member of the room to send messages"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create and save the message
        message = Message.objects.create(
            room=room,
            sender=sender,
            content=content
        )

        return Response({
            "message": "Message sent successfully",
            "message_id": str(message._id)
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
