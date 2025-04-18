from django import forms
from core.models import Room, RoommateProfile, RoomBooking, RoomContract, SupportTicket,Subscription, Review
from message.models import Message


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['title', 'description', 'location', 'price', 'available_from']
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
        }


class RoommateProfileForm(forms.ModelForm):
    class Meta:
        model = RoommateProfile
        fields = ['age', 'gender', 'occupation', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        