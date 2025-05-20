from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_payment, name='create_payment'),
    path('execute/', views.execute_payment, name='execute_payment'),
    path('cancel/', views.cancel_payment, name='cancel_payment'),
    path('ipn/', views.ipn_listener, name='ipn_listener'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
]