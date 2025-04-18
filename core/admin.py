from django.contrib import admin

from .models import Room, RoommateProfile, RoomBooking, RoomContract, SupportTicket,Subscription, Review

# Register your models here
admin.site.register(Room)
admin.site.register(RoommateProfile)
admin.site.register(RoomBooking)
admin.site.register(RoomContract)
admin.site.register(SupportTicket)
admin.site.register(Subscription)
admin.site.register(Review)