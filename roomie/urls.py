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
    path('logout/', views.logout_view, name='logout'),  # Custom logout page
    path('list-room/', views.list_room, name='list_room'),
    path('find-roommate/', views.find_roommate, name='find_roommate'),
    path('send-message/<int:user_id>/', views.send_message, name='send_message'),
    path('user-profile/<int:user_id>/', views.user_profile, name='user_profile'),  # User profile page
    path('messages/<int:user_id>/', views.messages_view, name='messages'),  # Messages page
    path('messages/<int:user_id>/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('list-room/', views.list_room, name='list_room'),  # URL for listing a room
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),  # Room details page
    path('filter-rooms/', views.filter_rooms, name='filter_rooms'),  # Advanced filter page
    path('room/<int:room_id>/book/', views.book_room, name='book_room'),
    path('room/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('update-booking/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),

    # Support Ticket System URLs
    path('support/', views.support_home, name='support_home'),
    path('support/submit/', views.submit_support_ticket, name='submit_support_ticket'),
    path('support/tickets/', views.view_support_tickets, name='view_support_tickets'),
    path('support/tickets/<int:ticket_id>/', views.view_support_ticket_detail, name='view_support_ticket_detail'),
    path('support/tickets/<int:ticket_id>/respond/', views.add_ticket_response, name='add_ticket_response'),
    path('support/tickets/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('support/tickets/<int:ticket_id>/reopen/', views.reopen_ticket, name='reopen_ticket'),

    # Dashboard URL
    path('dashboard/', views.dashboard, name='dashboard'),
]
