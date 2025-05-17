from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bson import ObjectId
from .models import Follow, User 
from spotify_app.models import Artist 
from .serializers import ArtistSerializer, FollowSerializer
from user_management.serializers import UserSerializer
from backend.utils import SchemaFactory
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

# Follow một người dùng hoặc nghệ sĩ khác
@SchemaFactory.post_schema(
    # item_id_param='user_id',
    request_example={
        "follower_id": "60a7cbbde1f4e9165c4e99d8",
        "target_id": "60a7cbbde1f4e9165c4e99d9",
        "target_type": "artist"
    },
    success_response={
        "status_code": 201,
        "message": "Follow successful."
    },
    error_responses=[
        {"status_code": 400, "description": "Missing follower_id, target_id or target_type."},
        {"status_code": 400, "description": "Invalid ID format."},
        {"status_code": 404, "description": "Follower or target not found."}
    ],
    description="API để một người dùng follow một người dùng hoặc nghệ sĩ khác.",
    request_serializer=FollowSerializer,
    response_serializer=None
)
@api_view(['POST'])
@permission_classes([AllowAny])
def follow_target(request):
    # Lấy dữ liệu từ request
    follower_id = request.data.get('follower_id')
    target_id = request.data.get('target_id')
    target_type = request.data.get('target_type')

    # Kiểm tra dữ liệu đầu vào
    if not all([follower_id, target_id, target_type]):
        return Response(
            {"error": "Missing follower_id, target_id or target_type."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate ID format
    try:
        follower_id = ObjectId(follower_id)
        target_id = ObjectId(target_id)
    except Exception as e:
        return Response(
            {"error": f"Invalid ID format: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate target_type
    if target_type not in ['user', 'artist']:
        return Response(
            {"error": "Invalid target_type. Must be 'user' or 'artist'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Kiểm tra follower tồn tại
        follower = User.objects.get(_id=follower_id)
        
        # Kiểm tra target tồn tại và tạo quan hệ follow
        if target_type == 'user':
            target = User.objects.get(_id=target_id)
            
            # Ngăn chặn follow chính mình
            if follower_id == target_id:
                return Response(
                    {"error": "Cannot follow yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Kiểm tra đã follow chưa
            if Follow.objects.filter(follower=follower, target_user=target).exists():
                return Response(
                    {"error": "Already following this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tạo follow relationship
            follow = Follow.objects.create(
                follower=follower,
                target_user=target
            )
        else:
            target = Artist.objects.get(_id=target_id)
            
            # Kiểm tra đã follow chưa
            if Follow.objects.filter(follower=follower, target_artist=target).exists():
                return Response(
                    {"error": "Already following this artist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tạo follow relationship
            follow = Follow.objects.create(
                follower=follower,
                target_artist=target
            )

        return Response({
            "message": "Follow successful.",
            "follow_id": str(follow._id),
            "follower_id": str(follower._id),
            "target_id": str(target_id),
            "target_type": target_type
        }, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response(
            {"error": "Follower not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except (Artist.DoesNotExist, User.DoesNotExist):
        return Response(
            {"error": "Target not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Lấy danh sách nghệ sĩ mà người dùng đã follow
get_followed_artists_schema = SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "message": "Followed artists fetched successfully.",
        "artists": [
            {
                "_id": "60a7cbbde1f4e9165c4e99d9",
                "name": "Artist Name",
                "image": "url_to_image",
                "genres": ["Pop", "Rock"]
            }
        ]
    },
    error_responses=[
        {"status_code": 400, "description": "Invalid user_id format."},
        {"status_code": 404, "description": "User not found."}
    ],
    description="API lấy danh sách các nghệ sĩ mà người dùng đã follow.",
    serializer=ArtistSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_followed_artists(request, user_id):
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return Response({"error": "Invalid user_id format."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(_id=user_obj_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tất cả follow relationship với artist
    follows = Follow.objects.filter(
        follower=user,
        target_artist__isnull=False
    ).select_related('target_artist')
    
    # Serialize dữ liệu artist
    artists = [follow.target_artist for follow in follows]
    serialized_artists = ArtistSerializer(artists, many=True).data

    return Response({
        "success": True,
        "count": len(serialized_artists),
        "message": "Followed artists fetched successfully.",
        "artists": serialized_artists
    }, status=status.HTTP_200_OK)


# Lấy danh sách người dùng mà user đã follow
@api_view(['GET'])
@permission_classes([AllowAny])
def get_followed_users(request, user_id):
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        return Response({"error": "Invalid user_id format."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(_id=user_obj_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lấy tất cả follow relationship với user
    follows = Follow.objects.filter(
        follower=user,
        target_user__isnull=False
    ).select_related('target_user')
    
    # Serialize dữ liệu user (cần tạo UserSerializer)
    users = [follow.target_user for follow in follows]
    serialized_users = UserSerializer(users, many=True).data  # Giả sử đã có UserSerializer

    return Response({
        "success": True,
        "count": len(serialized_users),
        "message": "Followed users fetched successfully.",
        "users": serialized_users
    }, status=status.HTTP_200_OK)