from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('customers/', views.customers, name='customers'),
    path('upload', views.parse_excel, name='upload'), 
    path('logout/', views.user_logout, name='logout'),
    path('create_message/', views.create_message, name='create_message'),
    path('message_sent/', views.message_sent, name='message_sent'),
]