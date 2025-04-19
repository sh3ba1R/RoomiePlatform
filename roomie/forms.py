from django import forms
from core.models import Room, RoommateProfile, RoomBooking, RoomContract, SupportTicket,Subscription, Review
from message.models import Message


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['title', 'location' , 'description', 'rent', 'available_from']
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

class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['room', 'start_date', 'end_date']


class RoomContractForm(forms.ModelForm):
    class Meta:
        model = RoomContract
        fields = ['room', 'user', 'contract_text', 'start_date', 'end_date']        

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['plan', 'payment_method']        

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['room', 'rating', 'comment']       


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'content']         