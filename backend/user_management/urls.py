from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('auth/token/refresh/', views.refresh_access_token, name='token_refresh'),
]