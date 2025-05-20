from django.urls import path
from . import roomviews
from . import messviews
from . import musicviews

urlpatterns = [
    # path('room/<str:room_id>/join', roomviews.add_user, name='add_user'),
    path('rooms/create/', roomviews.create_room, name='create_room'),
    path('rooms/find/<str:room_code>/', roomviews.find_room, name='find_room'),
    path('rooms/user/', roomviews.get_user_rooms, name='get_user_rooms'),
    path('rooms/<str:room_id>/join/', roomviews.join_room, name='join_room'),
    path('rooms/<str:room_id>/leave/', roomviews.leave_room, name='leave_room'),
    path('rooms/<str:room_id>/delete/', roomviews.delete_room, name='delete_room'),
    path('rooms/<str:room_id>/allusers/', roomviews.get_room_users, name='get_room_users'),
    path('rooms/<str:room_id>/messages/', messviews.get_messages, name='get_messages'),
    path('rooms/<str:room_id>/messages/send/', messviews.send_message, name='send_message'),
    path('rooms/<str:room_id>/state/', roomviews.get_room_state, name='get_room_state'),
    # path('room/<str:room_id>/leave', roomviews.remove_user, name='remove_user'),
    
    # Room playlist endpoints (simplified)
    path('rooms/<str:room_id>/playlist/', musicviews.get_room_playlist, name='get_room_playlist'),
    path('rooms/<str:room_id>/playlist/add/', musicviews.add_song_to_room_playlist, name='add_song_to_room_playlist'),
]
