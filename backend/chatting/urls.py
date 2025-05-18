from django.urls import path
from . import roomviews
from . import messviews

urlpatterns = [
    # path('room/<str:room_id>/join', roomviews.add_user, name='add_user'),
    path('rooms/create/', roomviews.create_room, name='create_room'),
    path('rooms/find/', roomviews.find_room, name='find_room'),
    path('rooms/<str:room_id>/join/', roomviews.join_room, name='join_room'),
    path('rooms/<str:room_id>/leave/', roomviews.leave_room, name='leave_room'),
    path('rooms/<str:room_id>/delete/', roomviews.delete_room, name='delete_room'),
    path('rooms/<str:room_id>/users/', roomviews.get_room_users, name='get_room_users'),
    path('rooms/<str:room_id>/messages/', messviews.get_messages, name='get_messages'),
    path('rooms/<str:room_id>/messages/send/', messviews.send_message, name='send_message'),
    # path('room/<str:room_id>/leave', roomviews.remove_user, name='remove_user'),
]
