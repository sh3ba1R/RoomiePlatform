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