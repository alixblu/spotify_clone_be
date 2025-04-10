from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='custom_login'),
    path('register/', views.custom_register, name='custom_register'),
    # path('callback/', views.spotify_callback, name='spotify_callback'),
]