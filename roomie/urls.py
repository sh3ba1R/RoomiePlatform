from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views
"""
URL Configuration for the Roomie Platform application.
This module defines the URL patterns that map to view functions in the application.
Django uses these patterns to route incoming HTTP requests to the appropriate view.
URL Patterns:
- '': Maps to the home view (homepage)
- 'register/': Maps to the user registration view
- 'login/': Maps to the user login view
- 'list-room/': Maps to the view for listing a room
- 'find-roommate/': Maps to the view for finding potential roommates
"""

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Custom logout page    path('list-room/', views.list_room, name='list_room'),
    path('find-roommate/', views.find_roommate, name='find_roommate'),
    path('send-message/<int:user_id>/', views.send_message, name='send_message'),
    path('user-profile/<int:user_id>/', views.user_profile, name='user_profile'),  # User profile page
    path('messages/<int:user_id>/', views.messages_view, name='messages'),  # Messages page
    path('list-room/', views.list_room, name='list_room'),  # URL for listing a room



]
