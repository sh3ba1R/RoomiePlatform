from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
	Room,
	RoomBooking,
	RoomContract,
	SupportTicket,
	Subscription,
	UserReview,
    RoomReview,
    #Message
)

# Register your models here
admin.site.register(User, UserAdmin)
admin.site.register(Room)
admin.site.register(RoomBooking)
admin.site.register(RoomContract)
admin.site.register(SupportTicket)
admin.site.register(Subscription)
admin.site.register(UserReview)
admin.site.register(RoomReview)
#admin.site.register(Message)

class CustomUserAdmin(UserAdmin):
    # Customize the admin interface for the User model
    list_display = ('username', 'email', 'account_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('account_type', 'is_active', 'is_staff')
    ordering = ('username',)

    # Enable the delete action
    actions = ['delete_selected']

# If you don't need the default Group model, you can unregister it
from django.contrib.auth.models import Group
admin.site.unregister(Group)