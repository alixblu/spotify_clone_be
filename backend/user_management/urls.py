from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('update_user/<str:user_id>/', views.update_user, name='update_user_with_id'),
    path('get_user_info/<str:user_id>/', views.get_user_by_id, name='getUserById'),
    path('auth/token/refresh/', views.refresh_access_token, name='token_refresh'),
    path('getallusers/', views.get_user_list, name='get_user_list'),
]