from django.urls import path
from . import views
from .views import CustomerUpdateView, CustomerDeleteView, SendMessageView
from .views import get_rain_affected_zips, get_wind_affected_zips

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('customers/', views.customers, name='customers'),
    path('upload', views.parse_excel, name='upload'), 
    path('logout/', views.user_logout, name='logout'),
    path('send_message/', views.send_message_view, name='send_message_view'),
    path('message_history/', views.message_history, name='message_history'),
    path('customer/<int:id>/', CustomerUpdateView.as_view(), name='customer'),
    path('customer/<int:id>/delete', CustomerDeleteView.as_view(), name='delete_customer'),
    path('customer/<int:id>/send_message', SendMessageView.as_view(), name='send_message'),
    path('bulk_message/', views.BulkMessageView.as_view(), name='bulk_message'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('rain_affected_zips/', views.rain_affected_zips, name='rain_affected_zips'),
    path('wind_affected_zips/', views.wind_affected_zips, name='wind_affected_zips'),
]