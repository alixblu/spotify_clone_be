from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from bson import ObjectId
from bson.errors import InvalidId
from .models import ArtistPerform, Artist, Song, FavoriteSong, User, FavoriteAlbum, Album, FavoritePlaylist, Playlist
from music_library.serializers import ArtistPerformSerializer, ArtistPerformByArtistSerializer, ArtistPerformBySongSerializer, FavoriteSongSerializer, SongSerializer, FavoriteSongCreateSerializer, FavoriteAlbumSerializer, FavoritePlaylistSerializer
from backend.utils import SchemaFactory
import traceback
from datetime import datetime
from spotify_app.permissionsCustom import IsAdminUser, IsAuthenticated


# ========================================  ARTISTPERFORM  ========================================
@SchemaFactory.post_schema(
    item_id_param="artist_id",
    request_example={
        "song_id": "663bb2f9e0d4f142c6f51499"
    },
    success_response={
        "message": "Thêm nghệ sĩ biểu diễn bài hát thành công",
        "artist_perform": {
            "_id": "663bb309e0d4f142c6f5149a",
            "artist_id": "663bb2e3e0d4f142c6f51498",
            "song_id": "663bb2f9e0d4f142c6f51499"
        }
    },
    error_responses=[
        {
            "name": "Thiếu song_id",
            "response": {"error": "Song ID is required."},
            "status_code": 400
        },
        {
            "name": "Nghệ sĩ đã biểu diễn",
            "response": {"error": "Nghệ sĩ đã biểu diễn bài hát này."},
            "status_code": 400
        },
        {
            "name": "Không tìm thấy",
            "response": {"error": "Artist or Song not found."},
            "status_code": 404
        }
    ],
    description="Thêm nghệ sĩ biểu diễn bài hát.",
    request_serializer=ArtistPerformSerializer,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def add_artist_performance(request, artist_id):
    # Lấy song_id từ dữ liệu yêu cầu (POST body)
    song_id = request.data.get('song_id')

    if not song_id:
        return Response(
            {"error": "Song ID is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra tính hợp lệ của ObjectId trước khi chuyển đổi
    if not ObjectId.is_valid(artist_id):
        return Response(
            {"error": "Invalid Artist ID format."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not ObjectId.is_valid(song_id):
        return Response(
            {"error": "Invalid Song ID format."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        artist_obj_id = ObjectId(artist_id)
        song_obj_id = ObjectId(song_id)
        print(f"DEBUG: artist_obj_id - {artist_obj_id}, song_obj_id - {song_obj_id}")
        # Kiểm tra sự tồn tại của artist và bài hát
        artist = Artist.objects.get(_id=artist_obj_id)
        song = Song.objects.get(_id=song_obj_id)
        print(f"DEBUG: Artist found - {artist}, Song found - {song}")
        # Kiểm tra trùng lặp
        if ArtistPerform.objects.filter(artist=artist, song=song).exists():
            return Response(
                {"error": "This artist already performed this song."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Chuẩn bị dữ liệu
        artist_perform_data = {
            'artist': artist_obj_id, 
            'song': song_obj_id,      
        }
        print(f"DEBUG: ArtistPerform data - {artist_perform_data}")
        # Khởi tạo và validate serializer
        serializer = ArtistPerformSerializer(data=artist_perform_data)
        serializer.is_valid(raise_exception=True)
        print(f"DEBUG: Serializer - {serializer}")
        # Lưu dữ liệu
        try:
            artist_perform = serializer.save()
            print(f"DEBUG: ArtistPerform saved - {artist_perform}")
            return Response({
                "message": "Thêm nghệ sĩ biểu diễn bài hát thành công",
                "artist_perform": {
                    "_id": str(artist_perform._id),
                    "artist_id": str(artist._id),
                    "song_id": str(song._id)
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as save_error:
            print(f"SAVE ERROR DETAILS: {str(save_error)}")
            print(f"TRACEBACK: {traceback.format_exc()}")
            return Response(
                {"error": f"Database save failed: {str(save_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except (Artist.DoesNotExist, Song.DoesNotExist):
        return Response(
            {"error": "Artist or Song not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as ve:
            return Response(
                {"error": f"Validation error: {str(ve)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"FULL ERROR: {error_msg}\n{traceback.format_exc()}")
        return Response(
            {"error": error_msg}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# LẤY DANH SÁCH BÀI HÁT DO NGHỆ SĨ BIỂU DIỄN
@SchemaFactory.retrieve_schema(
    item_id_param='artist_id',
    success_response={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "artist_id": "507f1f77bcf86cd799439011",
        "song_id": "60d5ec9cf8a1b4626e7d4e92"
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Artist performance not found."},
            "status_code": 404
        }
    ],
    description="Lấy danh sách bài hát của nghệ sĩ",
    serializer=ArtistPerformByArtistSerializer
    )
@api_view(['GET'])
@permission_classes([AllowAny])
def get_artist_performances(request, artist_id):
    if not ObjectId.is_valid(artist_id):
        return Response({"error": "Invalid artist ID format."}, status=400)

    artist_obj_id = ObjectId(artist_id)

    if not Artist.objects.filter(_id=artist_obj_id).exists():
        return Response({"error": "Artist not found."}, status=404)

    performances = ArtistPerform.objects.select_related('song').filter(artist=artist_obj_id)
    serializer = ArtistPerformByArtistSerializer(performances, many=True)
    return Response(serializer.data)



#  LẤY BÀI HÁT CÓ THÔNG TIN NGHỆ SĨ THEO ID BÀI HÁT
@SchemaFactory.retrieve_schema(
    item_id_param='song_id',
    success_response={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "artist": {
            "_id": "507f1f77bcf86cd799439011",
            "name": "Tên nghệ sĩ"
        },
        "song_id": "60d5ec9cf8a1b4626e7d4e92"
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Artist performance not found."},
            "status_code": 404
        }
    ],
    description="Lấy danh sách nghệ sĩ biểu diễn bài hát",
    serializer=ArtistPerformBySongSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_song_artists_performances(request, song_id):
    """
    Lấy danh sách nghệ sĩ biểu diễn bài hát (public)
    """
    if not ObjectId.is_valid(song_id):
        return Response({"error": "Invalid song ID format."}, status=400)

    song_obj_id = ObjectId(song_id)

    if not Song.objects.filter(_id=song_obj_id).exists():
        return Response({"error": "Song not found."}, status=404)

    performances = ArtistPerform.objects.select_related('artist', 'song').filter(song_id=ObjectId(song_id))
    serializer = ArtistPerformBySongSerializer(performances, many=True)
    return Response(serializer.data)


# XÓA ARTIST PERFORMANCE
@SchemaFactory.delete_schema(
    item_id_params=['artist_id', 'song_id'],
    success_response={"message": "Artist performance deleted successfully"},
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Artist performance not found"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "Invalid artist_id or song_id"},
            "status_code": 400
        }
    ],
    description="Xóa mối quan hệ nghệ sĩ-biểu diễn theo artist_id và song_id (chỉ admin)"
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_artist_performance(request, artist_id, song_id):
    """
    Xóa mối quan hệ nghệ sĩ biểu diễn bài hát (chỉ admin)
    """
    try:
        artist_obj_id = ObjectId(artist_id)
        song_obj_id = ObjectId(song_id)
    except Exception:
        return Response({"error": "Invalid artist_id or song_id"}, status=400)

    try:
        performance = ArtistPerform.objects.get(artist=artist_obj_id, song=song_obj_id)
        performance.delete()
        return Response({"message": "Artist performance deleted successfully"}, status=204)
    except ArtistPerform.DoesNotExist:
        return Response({"error": "Artist performance not found"}, status=404)



# =============================================  FAVORITE SONG ==============================================
#  Lấy danh sách bài hát yêu thích của người dùng
@SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "song": {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Tên bài hát"
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Favorite song not found."},
            "status_code": 404
        }
    ],
    description="Lấy danh sách bài hát yêu thích của người dùng",
    serializer=FavoriteSongSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_favorite_songs(request, user_id):
    """
    Lấy danh sách bài hát yêu thích của người dùng (public)
    """
    if not ObjectId.is_valid(user_id):
        return Response({"error": "Invalid user ID format."}, status=400)

    user_obj_id = ObjectId(user_id)

    if not FavoriteSong.objects.filter(user_id=user_obj_id).exists():
        return Response({"error": "User not found."}, status=404)

    favorite_songs = FavoriteSong.objects.select_related('song').filter(user_id=user_obj_id)
    serializer = FavoriteSongSerializer(favorite_songs, many=True)
    return Response(serializer.data)


# Lấy tổng số bài hát yêu thích của người dùng
@SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "name": "Bài hát đã thích",
        "description": "Tổng số bài hát đã thích: 5",
        "total": 5,
        "songs": [
            {
                "_id": "507f1f77bcf86cd799439011",
                "title": "Tên bài hát 1"
            },
            {
                "_id": "507f1f77bcf86cd799439012",
                "title": "Tên bài hát 2"
            }
        ]
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "User not found."},
            "status_code": 404
        }
    ],
    description="Lấy tổng số bài hát yêu thích và danh sách bài hát của người dùng",
    serializer=FavoriteSongSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_favorite_songs_summary(request, user_id):
    """
    Lấy tổng số bài hát yêu thích và danh sách bài hát của người dùng (public)
    """
    try:
        # Validate user_id
        if not ObjectId.is_valid(user_id):
            return Response({"error": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

        user_obj_id = ObjectId(user_id)

        # Check if user exists
        if not User.objects.filter(_id=user_obj_id).exists():
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get favorite songs with related song data
        favorite_songs = FavoriteSong.objects.select_related('song').filter(user_id=user_obj_id)
        total_songs = favorite_songs.count()

        # Prepare song data with proper ObjectId serialization
        songs_data = []
        for fav_song in favorite_songs:
            song = fav_song.song
            songs_data.append({
                "_id": str(song._id),
                "title": song.title,
                # "artist": song.artist.name if hasattr(song, 'artist') else None,
            })

        response_data = {
            "success": True,
            "name": "Bài hát đã thích",
            "description": total_songs,
            "total": total_songs,
            "songs": songs_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(
            {"error": "Đã xảy ra lỗi khi xử lý yêu cầu"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#  Thêm bài hát vào danh sách yêu thích
@SchemaFactory.post_schema(
    item_id_param="user_id",
    request_example={"song_id": "507f1f77bcf86cd799439011"},
    success_response={
        "message": "Thêm vào danh sách yêu thích thành công",
        "data": {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": "507f1f77bcf86cd799439010",
            "song_id": "507f1f77bcf86cd799439011",
            "added_at": "2023-01-01T00:00:00Z"
        }
    },
    error_responses=[
        {
            "name": "Đã tồn tại",
            "response": {"error": "Bài hát đã có trong danh sách yêu thích"},
            "status_code": 400
        },
        {
            "name": "Không tìm thấy user hoặc bài hát",
            "response": {"error": "User hoặc bài hát không tồn tại"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        }
    ],
    description="Thêm bài hát vào danh sách yêu thích của user",
    request_serializer=SongSerializer,
)
# @api_view(['POST'])
# @permission_classes([IsAdminUser | IsAuthenticated])
# def create_favorite_songs(request, user_id):
#     print(f"DEBUG: Received request - {request}")
#     print(f"DEBUG: Received request.user.is_authenticated - {request.user.is_authenticated}")
#     try:
#         # Chuyển đổi và kiểm tra ObjectId
#         user_obj_id = ObjectId(user_id)
#     except:
#         return Response(
#             {"error": "User ID không đúng định dạng"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Kiểm tra user tồn tại
#     try:
#         user = User.objects.get(_id=user_obj_id)
#         print(f"DEBUG: User found - {user}")
#     except User.DoesNotExist:
#         return Response(
#             {"error": "User không tồn tại"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     print("request.user", request.user)  # In thông tin người dùng để kiểm tra
#     print("request.user.is_authenticated", request.user.is_authenticated)  # In thông tin người dùng để kiểm tra
#     # Kiểm tra nếu người dùng chưa đăng nhập
#     # if not request.user.is_authenticated:
#     #     return Response({"error": "Bạn cần đăng nhập để thực hiện thao tác này"}, status=status.HTTP_401_UNAUTHORIZED)
    
#     print("user._id", user._id)  # In thông tin người dùng để kiểm tra
#     print("request.user.role", request.user.role)  # In thông tin người dùng để kiểm tra
#     print("request.user._id", request.user._id)  # In thông tin người dùng để kiểm tra
#     # Kiểm tra nếu user đang thao tác có id trùng với user_id cần thêm vào
#     if str(request.user._id) != user_id:
#         return Response({"error": "Bạn không có quyền thực hiện thao tác này"}, status=status.HTTP_403_FORBIDDEN)

#     # Validate song_id
#     song_id = request.data.get('song_id')
#     if not song_id:
#         return Response(
#             {"error": "song_id là bắt buộc"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         song_obj_id = ObjectId(song_id)
#     except:
#         return Response(
#             {"error": "Song ID không đúng định dạng"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Kiểm tra bài hát tồn tại
#     try:
#         song = Song.objects.get(_id=song_obj_id)
#     except Song.DoesNotExist:
#         return Response(
#             {"error": "Bài hát không tồn tại"},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # Kiểm tra đã tồn tại trong danh sách yêu thích chưa
#     if FavoriteSong.objects.filter(user=user, song=song).exists():
#         return Response(
#             {"error": "Bài hát đã có trong danh sách yêu thích"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Tạo dữ liệu FavoriteSong trước khi khởi tạo serializer
#     try:
#         # Tạo bản ghi mới trực tiếp bằng model
#         # favorite = FavoriteSong.objects.create(user=user, song=song)
#         # Tạo bản ghi mới với _id tự động tạo bởi MongoDB
#         favorite = FavoriteSong(
#             _id=ObjectId(),  # Tạo mới ObjectId
#             user=user, 
#             song=song, 
#             added_at=datetime.now()
#         )
#         print("favorite", favorite)
#         favorite.save()
#         print(f"DEBUG: Created favorite - {favorite}")
        
#         return Response({
#             "message": "Thêm vào danh sách yêu thích thành công",
#             "data": {
#                 "_id": str(favorite._id),
#                 "user_id": str(favorite.user._id),
#                 "song_id": str(favorite.song._id),
#                 "added_at": favorite.added_at.isoformat()
#             }
#         }, status=status.HTTP_201_CREATED)
        
#     except Exception as e:
#         print(f"ERROR: Failed to create favorite - {str(e)}")
#         print(traceback.format    _exc())
#         return Response(
#             {"error": "Lỗi hệ thống khi thêm vào danh sách yêu thích"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


@api_view(['POST'])
@permission_classes([IsAdminUser | IsAuthenticated])
def create_favorite_songs(request, user_id):
    try:
        user_obj_id = ObjectId(user_id)
        user = User.objects.get(_id=user_obj_id)
    except:
        return Response(
            {"error": "User ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != user_id and request.user.role != 'admin':
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"},
            status=status.HTTP_403_FORBIDDEN
        )

    song_id = request.data.get('song_id')
    if not song_id:
        return Response(
            {"error": "Thiếu song_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        song_obj_id = ObjectId(song_id)
        song = Song.objects.get(_id=song_obj_id)
    except:
        return Response(
            {"error": "Song ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if FavoriteSong.objects.filter(user=user, song=song).exists():
        return Response(
            {"error": "Bài hát đã có trong danh sách yêu thích"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        print(f"DEBUG: user - {user}, song - {song}")
        # Tạo bản ghi trực tiếp bằng model thay vì serializer
        favorite_song = FavoriteSong.objects.create(
            user=user,
            song=song
        )
        print(f"DEBUG: Created favorite song - {favorite_song}")
        
        return Response({
            "message": "Thêm vào danh sách yêu thích thành công",
            # "data": {
            #     "_id": str(favorite_song._id),
            #     "user_id": str(favorite_song.user._id),
            #     "song_id": str(favorite_song.song._id),
            #     "added_at": favorite_song.added_at.isoformat()
            # }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {"error": "Lỗi khi thêm vào danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# Xóa bài hát khỏi danh sách yêu thích
@SchemaFactory.delete_schema(
    item_id_params="user_id",
    success_response={
        "message": "Xóa bài hát khỏi danh sách yêu thích thành công",
        "data": {
            "deleted_count": 1
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Bài hát không có trong danh sách yêu thích"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        },
        {
            "name": "Không có quyền",
            "response": {"error": "Không có quyền thực hiện thao tác này"},
            "status_code": 403
        }
    ],
    description="Xóa bài hát khỏi danh sách yêu thích của user",
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser | IsAuthenticated])
def delete_favorite_song(request, user_id):
    try:
        # Validate user ID
        user_obj_id = ObjectId(user_id)
        user = User.objects.get(_id=user_obj_id)
    except:
        return Response(
            {"error": "User ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != user_id and request.user.role != 'admin':
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"},
            status=status.HTTP_403_FORBIDDEN
        )

    song_id = request.query_params.get('song_id')
    if not song_id:
        return Response(
            {"error": "Thiếu song_id trong query parameters"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        song_obj_id = ObjectId(song_id)
        song = Song.objects.get(_id=song_obj_id)
    except:
        return Response(
            {"error": "Song ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Tìm và xóa bản ghi
        deleted_count = FavoriteSong.objects.filter(user=user, song=song).delete()[0]
        
        if deleted_count == 0:
            return Response(
                {"error": "Bài hát không có trong danh sách yêu thích"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response({
            "message": "Xóa bài hát khỏi danh sách yêu thích thành công",
            "data": {
                "deleted_count": deleted_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(
            {"error": "Lỗi khi xóa bài hát khỏi danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# =============================================  FAVORITE ALBUM ==============================================
@SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "album": {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Tên album"
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Favorite album not found."},
            "status_code": 404
        }
    ],
    description="Lấy danh sách album yêu thích của người dùng",
    serializer=FavoriteAlbumSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_favorite_albums(request, user_id):
    """
    Lấy danh sách album yêu thích của người dùng (public)
    """
    if not ObjectId.is_valid(user_id):
        return Response({"error": "Invalid user ID format."}, status=400)

    user_obj_id = ObjectId(user_id)

    if not User.objects.filter(_id=user_obj_id).exists():
        return Response({"error": "User not found."}, status=404)

    favorite_albums = FavoriteAlbum.objects.select_related('album').filter(user_id=user_obj_id)
    serializer = FavoriteAlbumSerializer(favorite_albums, many=True)
    return Response(serializer.data)


@SchemaFactory.post_schema(
    item_id_param="user_id",
    request_example={"album_id": "507f1f77bcf86cd799439011"},
    success_response={
        "message": "Thêm vào danh sách yêu thích thành công",
        "data": {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": "507f1f77bcf86cd799439010",
            "album_id": "507f1f77bcf86cd799439011",
            "added_at": "2023-01-01T00:00:00Z"
        }
    },
    error_responses=[
        {
            "name": "Đã tồn tại",
            "response": {"error": "Album đã có trong danh sách yêu thích"},
            "status_code": 400
        },
        {
            "name": "Không tìm thấy user hoặc album",
            "response": {"error": "User hoặc album không tồn tại"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        }
    ],
    description="Thêm album vào danh sách yêu thích của user",
    request_serializer=FavoriteAlbumSerializer,
)
@api_view(['POST'])
@permission_classes([IsAdminUser | IsAuthenticated])
def create_favorite_album(request, user_id):
    try:
        user_obj_id = ObjectId(user_id)
        user = User.objects.get(_id=user_obj_id)
    except:
        return Response(
            {"error": "User ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != user_id and request.user.role != 'admin':
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"},
            status=status.HTTP_403_FORBIDDEN
        )

    album_id = request.data.get('album_id')
    if not album_id:
        return Response(
            {"error": "Thiếu album_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        album_obj_id = ObjectId(album_id)
        album = Album.objects.get(_id=album_obj_id)
    except:
        return Response(
            {"error": "Album ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if FavoriteAlbum.objects.filter(user=user, album=album).exists():
        return Response(
            {"error": "Album đã có trong danh sách yêu thích"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        favorite_album = FavoriteAlbum.objects.create(
            user=user,
            album=album
        )
        
        return Response({
            "message": "Thêm album vào danh sách yêu thích thành công",
            "data": FavoriteAlbumSerializer(favorite_album).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(
            {"error": "Lỗi khi thêm album vào danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# Xóa album khỏi danh sách yêu thích
@SchemaFactory.delete_schema(
    item_id_params="favorite_album_id",
    success_response={
        "message": "Xóa album khỏi danh sách yêu thích thành công",
        "data": {
            "deleted_count": 1
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Album không có trong danh sách yêu thích"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        },
        {
            "name": "Không có quyền",
            "response": {"error": "Không có quyền xóa album này"},
            "status_code": 403
        }
    ],
    description="Xóa album khỏi danh sách yêu thích của user",
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_favorite_album(request, favorite_album_id):
    try:
        favorite_album_obj_id = ObjectId(favorite_album_id)
        favorite_album = FavoriteAlbum.objects.get(_id=favorite_album_obj_id)
    except:
        return Response(
            {"error": "Favorite album ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != str(favorite_album.user._id) and request.user.role != 'admin':
        return Response(
            {"error": "Bạn không có quyền xóa album này khỏi danh sách yêu thích"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Lưu thông tin trước khi xóa để trả về response
        deleted_album_info = {
            "album_id": str(favorite_album.album._id),
            "album_title": favorite_album.album.title
        }
        
        favorite_album.delete()
        
        return Response({
            "message": "Xóa album khỏi danh sách yêu thích thành công",
            "data": {
                "deleted_count": 1,
                "deleted_album": deleted_album_info
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(
            {"error": "Lỗi khi xóa album khỏi danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# =============================================  FAVORITE PLAYLIST ==============================================
@SchemaFactory.retrieve_schema(
    item_id_param='user_id',
    success_response={
        "_id": "60d5ec9cf8a1b4626e7d4e92",
        "playlist": {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Tên playlist"
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Favorite playlist not found."},
            "status_code": 404
        }
    ],
    description="Lấy danh sách playlist yêu thích của người dùng",
    serializer=FavoritePlaylistSerializer
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_favorite_playlists(request, user_id):
    """
    Lấy danh sách playlist yêu thích của người dùng (public)
    """
    if not ObjectId.is_valid(user_id):
        return Response({"error": "Invalid user ID format."}, status=400)

    user_obj_id = ObjectId(user_id)

    if not User.objects.filter(_id=user_obj_id).exists():
        return Response({"error": "User not found."}, status=404)

    favorite_playlists = FavoritePlaylist.objects.select_related('playlist').filter(user_id=user_obj_id)
    serializer = FavoritePlaylistSerializer(favorite_playlists, many=True)
    return Response(serializer.data)


# Thêm playlist vào danh sách yêu thích
@SchemaFactory.post_schema(
    item_id_param="user_id",
    request_example={"playlist_id": "507f1f77bcf86cd799439011"},
    success_response={
        "message": "Thêm vào danh sách yêu thích thành công",
        "data": {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": "507f1f77bcf86cd799439010",
            "playlist_id": "507f1f77bcf86cd799439011",
            "added_at": "2023-01-01T00:00:00Z"
        }
    },
    error_responses=[
        {
            "name": "Đã tồn tại",
            "response": {"error": "Playlist đã có trong danh sách yêu thích"},
            "status_code": 400
        },
        {
            "name": "Không tìm thấy user hoặc playlist",
            "response": {"error": "User hoặc playlist không tồn tại"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        }
    ],
    description="Thêm playlist vào danh sách yêu thích của user",
    request_serializer=FavoritePlaylistSerializer,
)
@api_view(['POST'])
@permission_classes([IsAdminUser | IsAuthenticated])
def create_favorite_playlist(request, user_id):
    try:
        user_obj_id = ObjectId(user_id)
        user = User.objects.get(_id=user_obj_id)
    except:
        return Response(
            {"error": "User ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != user_id and request.user.role != 'admin':
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"},
            status=status.HTTP_403_FORBIDDEN
        )

    playlist_id = request.data.get('playlist_id')
    if not playlist_id:
        return Response(
            {"error": "Thiếu playlist_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        playlist_obj_id = ObjectId(playlist_id)
        playlist = Playlist.objects.get(_id=playlist_obj_id)
    except:
        return Response(
            {"error": "Playlist ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if FavoritePlaylist.objects.filter(user=user, playlist=playlist).exists():
        return Response(
            {"error": "Playlist đã có trong danh sách yêu thích"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        favorite_playlist = FavoritePlaylist.objects.create(
            user=user,
            playlist=playlist
        )
        
        return Response({
            "message": "Thêm playlist vào danh sách yêu thích thành công",
            "data": FavoritePlaylistSerializer(favorite_playlist).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(
            {"error": "Lỗi khi thêm playlist vào danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

  
# Xóa playlist khỏi danh sách yêu thích
@SchemaFactory.delete_schema(
    item_id_params="favorite_playlist_id",
    success_response={
        "message": "Xóa playlist khỏi danh sách yêu thích thành công",
        "data": {
            "deleted_count": 1
        }
    },
    error_responses=[
        {
            "name": "Không tìm thấy",
            "response": {"error": "Playlist không có trong danh sách yêu thích"},
            "status_code": 404
        },
        {
            "name": "ID không hợp lệ",
            "response": {"error": "ID không đúng định dạng"},
            "status_code": 400
        },
        {
            "name": "Không có quyền",
            "response": {"error": "Không có quyền xóa playlist này"},
            "status_code": 403
        }
    ],
    description="Xóa playlist khỏi danh sách yêu thích của user",
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_favorite_playlist(request, favorite_playlist_id):
    try:
        favorite_playlist_obj_id = ObjectId(favorite_playlist_id)
        favorite_playlist = FavoritePlaylist.objects.get(_id=favorite_playlist_obj_id)
    except:
        return Response(
            {"error": "Favorite playlist ID không hợp lệ hoặc không tồn tại"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra quyền
    if str(request.user._id) != str(favorite_playlist.user._id) and request.user.role != 'admin':
        return Response(
            {"error": "Bạn không có quyền xóa playlist này khỏi danh sách yêu thích"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Lưu thông tin trước khi xóa để trả về response
        deleted_playlist_info = {
            "playlist_id": str(favorite_playlist.playlist._id),
            "playlist_title": favorite_playlist.playlist.title
        }
        
        favorite_playlist.delete()
        
        return Response({
            "message": "Xóa playlist khỏi danh sách yêu thích thành công",
            "data": {
                "deleted_count": 1,
                "deleted_playlist": deleted_playlist_info
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(
            {"error": "Lỗi khi xóa playlist khỏi danh sách yêu thích"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )