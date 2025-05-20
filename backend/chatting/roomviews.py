import datetime
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId

from django.http import JsonResponse
from backend.utils import SchemaFactory
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import ChatRoom, Message
from user_management.models import User
from rest_framework.pagination import LimitOffsetPagination

@SchemaFactory.post_schema(
    request_example={
        "name": "Music Chat",
        "description": "A room to discuss music trends and artists.",
        "host": "68126721a848889c35046cf3"
    },
    success_response={
        "message": "Room created successfully.",
        "room_id": "507f1f77bcf86cd799439012"
    },
    error_responses=[
        {
            "name": "Missing Required Fields",
            "response": {"error": "Room name is required."},
            "status_code": 400
        },
        {
            "name": "Host Not Found",
            "response": {"error": "Host user with ID {host_id} does not exist"},
            "status_code": 400
        },
        {
            "name": "Invalid ID Format",
            "response": {"error": "Invalid ID format: {error_message}"},
            "status_code": 400
        }
    ],
    description="Create a new chat room with the specified name, description, and host"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_room(request):
    """
    Create a new chat room.
    """
    try:
        name = request.data.get('name')
        description = request.data.get('description', '')
        host_id = request.data.get('host')  # Get the host ID from request

        if not name:
            return Response({"error": "Room name is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not host_id:
            return Response({"error": "Host user is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert string IDs to ObjectId
        try:
            host_id = ObjectId(host_id)
        except Exception as e:
            return Response({"error": f"Invalid ID format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that the host user exists
        try:
            host_user = User.objects.get(_id=host_id)
        except User.DoesNotExist:
            return Response({"error": f"Host user with ID {host_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error finding host user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create the room with all required fields
        try:
            room = ChatRoom.objects.create(
                name=name,
                description=description,
                host=host_user,
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_active=True
            )
            
            # Add the host to the room's users list
            room.users.add(host_user)
            room.save()

            return Response({
                "message": "Room created successfully.",
                "room_id": str(room._id),
                "name": room.name,
                "description": room.description,
                "host": {
                    "_id": str(room.host._id),
                    "name": room.host.name,
                },
                "created_at": room.created_at.isoformat(),
                "is_active": room.is_active,
                "is_host": True
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            print(f"Error creating room: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": f"Error creating room: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        import traceback
        print(f"Unexpected error in create_room: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.list_schema(
    item_example={
        "status": "success",
        "room_id": "507f1f77bcf86cd799439011",
        "name": "Music Chat",
        "host": "507f1f77bcf86cd799439012"
    },
    description="Find a chat room by its room code (last 6 characters of room ID)",
    pagination=False,
    search_fields=None
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def find_room(request, room_code=None):
    try:
        # Get room_code from URL parameter or request data
        room_code = room_code or request.data.get('room_code')
        if not room_code:
            return Response({"error": "Room code is required"}, status=status.HTTP_400_BAD_REQUEST)

        rooms = ChatRoom.objects.all()
        # Filter manually by matching the last 6 characters of the ObjectId
        for room in rooms:
            if str(room._id)[-6:] == room_code:
                return Response({
                    "status": "success",
                    "room_id": str(room._id),
                    "name": room.name,
                    "host": str(room.host._id),
                })
        return Response({"status": "not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.post_schema(
    request_example={
        "user_id": "68126740a848889c35046cf4"
    },
    success_response={
        "message": "Successfully joined the room",
        "room_id": "507f1f77bcf86cd799439011"
    },
    error_responses=[
        {
            "name": "Room Not Found",
            "response": {"error": "Room not found"},
            "status_code": 404
        },
        {
            "name": "User Not Found",
            "response": {"error": "User not found"},
            "status_code": 404
        },
        {
            "name": "User Banned",
            "response": {"error": "You are banned from this room"},
            "status_code": 403
        },
        {
            "name": "Already Joined",
            "response": {"error": "You are already a member of this room"},
            "status_code": 400
        }
    ],
    description="Join a chat room. Checks if user is banned before allowing join."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def join_room(request, room_id):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is banned
        if user in room.ban_list.all():
            return Response({"error": "You are banned from this room"}, status=status.HTTP_403_FORBIDDEN)

        # Check if user is already in the room
        if user in room.users.all():
            return Response({"error": "You are already a member of this room"}, status=status.HTTP_400_BAD_REQUEST)

        # Add user to room
        room.users.add(user)
        room.save()

        return Response({
            "message": "Successfully joined the room",
            "room_id": str(room._id)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.list_schema(
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "username": "john_doe",
        "email": "john@example.com",
        "is_host": True
    },
    description="Get all users in a chat room",
    pagination=True
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_room_users(request, room_id):
    try:
        # Verify room exists
        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all users in the room
        users = room.users.all()
        
        # Apply pagination
        paginator = LimitOffsetPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        
        # Format response
        user_list = [{
            "_id": str(user._id),
            "username": user.username,
            "email": user.email,
            "is_host": user == room.host
        } for user in paginated_users]

        return Response({
            "count": users.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": user_list
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.post_schema(
    request_example={
        "user_id": "68126740a848889c35046cf4"
    },
    success_response={
        "message": "Successfully left the room",
        "room_id": "507f1f77bcf86cd799439011"
    },
    error_responses=[
        {
            "name": "Room Not Found",
            "response": {"error": "Room not found"},
            "status_code": 404
        },
        {
            "name": "User Not Found",
            "response": {"error": "User not found"},
            "status_code": 404
        },
        {
            "name": "User Not in Room",
            "response": {"error": "You are not a member of this room"},
            "status_code": 400
        },
        {
            "name": "Host Cannot Leave",
            "response": {"error": "Room host cannot leave the room"},
            "status_code": 400
        }
    ],
    description="Leave a chat room. Room host cannot leave the room."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def leave_room(request, room_id):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is in the room
        if user not in room.users.all():
            return Response({"error": "You are not a member of this room"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is the host
        if user == room.host:
            return Response({"error": "Room host cannot leave the room"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove user from room
        room.users.remove(user)
        room.save()

        return Response({
            "message": "Successfully left the room",
            "room_id": str(room._id)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.post_schema(
    request_example={
        "user_id": "68126740a848889c35046cf4"
    },
    success_response={
        "message": "Room and all its messages deleted successfully",
        "room_id": "507f1f77bcf86cd799439011"
    },
    error_responses=[
        {
            "name": "Room Not Found",
            "response": {"error": "Room not found"},
            "status_code": 404
        },
        {
            "name": "User Not Found",
            "response": {"error": "User not found"},
            "status_code": 404
        },
        {
            "name": "Not Authorized",
            "response": {"error": "Only room host can delete the room"},
            "status_code": 403
        }
    ],
    description="Delete a chat room and all its messages. Only the room host can delete the room."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def delete_room(request, room_id):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = ChatRoom.objects.get(_id=ObjectId(room_id))
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is the host
        if user != room.host:
            return Response({"error": "Only room host can delete the room"}, status=status.HTTP_403_FORBIDDEN)

        # Store room ID for response before deletion
        room_id_str = str(room._id)

        # Delete all messages in the room
        Message.objects.filter(room=room).delete()

        # Delete the room
        room.delete()

        return Response({
            "message": "Room and all its messages deleted successfully",
            "room_id": room_id_str
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@SchemaFactory.list_schema(
    search_fields= ["user_id"],
    item_example={
        "_id": "507f1f77bcf86cd799439011",
        "name": "Music Chat",
        "description": "A room to discuss music trends and artists.",
        "host": {
            "_id": "507f1f77bcf86cd799439012",
            "name": "john_doe"
        },
        "created_at": "2025-05-18T08:30:00Z",
        "is_active": True
    },
    description="Get all rooms that a user is participating in",
    pagination=True
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_rooms(request):
    """
    Get all rooms that a user is participating in.
    """
    try:
        user_id = request.query_params.get('user_id')
        print(f"Received request for user_id: {user_id}")
        
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(_id=ObjectId(user_id))
            print(f"Found user: {user.name}")
        except User.DoesNotExist:
            print(f"User not found with ID: {user_id}")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error finding user: {str(e)}")
            return Response({"error": f"Error finding user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get all rooms where the user is either a member or the host
        try:
            rooms = ChatRoom.objects.filter(users=user).order_by('-created_at')
            print(f"Found {rooms.count()} rooms for user")
        except Exception as e:
            print(f"Error querying rooms: {str(e)}")
            return Response({"error": f"Error querying rooms: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Apply pagination
        paginator = LimitOffsetPagination()
        try:
            paginated_rooms = paginator.paginate_queryset(rooms, request)
        except Exception as e:
            print(f"Error paginating rooms: {str(e)}")
            return Response({"error": f"Error paginating rooms: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Format response
        try:
            room_list = [{
                "_id": str(room._id),
                "name": room.name,
                "description": room.description,
                "host": {
                    "_id": str(room.host._id),
                    "name": room.host.name
                },
                "created_at": room.created_at.isoformat(),
                "is_active": room.is_active,
                "is_host": str(room.host._id) == user_id
            } for room in paginated_rooms]

            response_data = {
                "count": rooms.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": room_list
            }
            print(f"Returning response with {len(room_list)} rooms")
            return Response(response_data)
        except Exception as e:
            print(f"Error formatting response: {str(e)}")
            return Response({"error": f"Error formatting response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        import traceback
        print(f"Unexpected error in get_user_rooms: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

