from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('list-room/', views.list_room, name='list_room'),
    path('find-roommate/', views.find_roommate, name='find_roommate'),
]
