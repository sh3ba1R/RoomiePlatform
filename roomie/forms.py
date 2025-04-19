from django import forms
from django.contrib.auth.forms import AuthenticationForm
from core.models import Room, RoommateProfile, RoomBooking, RoomContract, SupportTicket, Subscription, Review
from message.models import Message


class RoomieForms:
    """
    A comprehensive class containing all form definitions for the Roomie platform.
    
    This class centralizes all forms used throughout the application, organizing
    them as inner classes for better code organization and management. Each inner 
    class handles a specific form type while sharing the same namespace.
    
    The forms include:
    - Room listings (RoomForm)
    - Roommate profiles (RoommateProfileForm)
    - Room bookings (RoomBookingForm)
    - Room contracts (RoomContractForm)
    - Support tickets (SupportTicketForm)
    - Subscriptions (SubscriptionForm)
    - Reviews (ReviewForm)
    - Messages (MessageForm)
    - Login (LoginForm)
    """
    
    class RoomForm(forms.ModelForm):
        """
        Form for creating and updating Room listings.

        This form is based on the Room model and includes fields for creating
        or editing room advertisements on the platform.

        Fields:
            - title: Title of the room listing
            - description: Detailed description of the room
            - location: Geographic location of the room
            - price: Monthly rent price
            - available_from: Date when the room becomes available

        Widgets:
            - available_from: Uses a date input widget for better date selection
        """
        class Meta:
            model = Room
            fields = ['title', 'location' , 'description', 'rent', 'available_from']
            widgets = {
                'available_from': forms.DateInput(attrs={'type': 'date'}),
            }

    class RoommateProfileForm(forms.ModelForm):
        """
        Form for creating or updating a roommate profile.

        This form is linked to the RoommateProfile model and includes fields
        for basic personal information such as age, gender, occupation, and bio.
        The bio field is rendered as a text area with 4 rows for better user experience.
        """
        class Meta:
            model = RoommateProfile
            fields = ['age', 'gender', 'occupation', 'bio']
            widgets = {
                'bio': forms.Textarea(attrs={'rows': 4}),
            }

    class RoomBookingForm(forms.ModelForm):
        """
        Form for booking rooms.
        
        Allows users to select a room and specify the booking period.
        """
        class Meta:
            model = RoomBooking
            fields = ['room', 'start_date', 'end_date']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date'}),
                'end_date': forms.DateInput(attrs={'type': 'date'}),
            }

    class RoomContractForm(forms.ModelForm):
        """
        Form for creating room rental contracts.
        
        Allows creation of legally binding contracts between users and room owners.
        """
        class Meta:
            model = RoomContract
            fields = ['room', 'user', 'contract_text', 'start_date', 'end_date']
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date'}),
                'end_date': forms.DateInput(attrs={'type': 'date'}),
                'contract_text': forms.Textarea(attrs={'rows': 6}),
            }

    class SupportTicketForm(forms.ModelForm):
        """
        Form for creating support tickets.
        
        Allows users to report issues or request assistance.
        """
        class Meta:
            model = SupportTicket
            fields = ['subject', 'message']
            widgets = {
                'message': forms.Textarea(attrs={'rows': 5}),
            }

    class SubscriptionForm(forms.ModelForm):
        """
        Form for managing subscription plans.
        
        Allows users to select a subscription plan and payment method.
        """
        class Meta:
            model = Subscription
            fields = ['plan', 'payment_method']

    class ReviewForm(forms.ModelForm):
        """
        Form for submitting room reviews.
        
        Allows users to rate and comment on rooms they've stayed in.
        """
        class Meta:
            model = Review
            fields = ['room', 'rating', 'comment']
            widgets = {
                'comment': forms.Textarea(attrs={'rows': 4}),
            }

    class MessageForm(forms.ModelForm):
        """
        Form for sending messages to other users.
        
        Allows communication between roommates, tenants, and landlords.
        """
        class Meta:
            model = Message
            fields = ['recipient', 'content']
            widgets = {
                'content': forms.Textarea(attrs={'rows': 3}),
            }

    class LoginForm(AuthenticationForm):
        """
        Form for user authentication.
        
        This form extends Django's built-in AuthenticationForm to provide
        username and password authentication functionality with Bootstrap styling.
        
        Fields:
            - username: User's username for authentication
            - password: User's password for authentication
        """
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add Bootstrap classes to form fields
            self.fields['username'].widget.attrs.update({
                'class': 'form-control', 
                'placeholder': 'Enter your username'
            })
            self.fields['password'].widget.attrs.update({
                'class': 'form-control', 
                'placeholder': 'Enter your password'
            })


class RoomieFormFactory:
    """
    A centralized factory class for creating all forms used in the Roomie platform.
    
    This factory provides methods to generate different types of forms used throughout 
    the application, making form instantiation consistent and centralized.
    """
    
    def create_login_form(self, request=None, data=None):
        """
        Creates a form for user authentication.
        
        Args:
            request: The current request (required for AuthenticationForm)
            data: Form data for binding (optional)
            
        Returns:
            An instance of the Login form
        """
        return RoomieForms.LoginForm(request=request, data=data)
    
    def create_room_form(self, data=None, instance=None):
        """
        Creates a form for room listings.
        
        Args:
            data: Form data for binding (optional)
            instance: Room instance to edit (optional)
            
        Returns:
            An instance of the Room form
        """
        return RoomieForms.RoomForm(data=data, instance=instance)
    
    def create_profile_form(self, data=None, instance=None):
        """
        Creates a form for roommate profiles.
        
        Args:
            data: Form data for binding (optional)
            instance: RoommateProfile instance to edit (optional)
            
        Returns:
            An instance of the RoommateProfile form
        """
        return RoomieForms.RoommateProfileForm(data=data, instance=instance)
    
    def create_booking_form(self, data=None, instance=None):
        """
        Creates a form for room bookings.
        
        Args:
            data: Form data for binding (optional)
            instance: RoomBooking instance to edit (optional)
            
        Returns:
            An instance of the RoomBooking form
        """
        return RoomieForms.RoomBookingForm(data=data, instance=instance)
    
    def create_contract_form(self, data=None, instance=None):
        """
        Creates a form for room contracts.
        
        Args:
            data: Form data for binding (optional)
            instance: RoomContract instance to edit (optional)
            
        Returns:
            An instance of the RoomContract form
        """
        return RoomieForms.RoomContractForm(data=data, instance=instance)
    
    def create_support_ticket_form(self, data=None, instance=None):
        """
        Creates a form for support tickets.
        
        Args:
            data: Form data for binding (optional)
            instance: SupportTicket instance to edit (optional)
            
        Returns:
            An instance of the SupportTicket form
        """
        return RoomieForms.SupportTicketForm(data=data, instance=instance)
    
    def create_subscription_form(self, data=None, instance=None):
        """
        Creates a form for subscriptions.
        
        Args:
            data: Form data for binding (optional)
            instance: Subscription instance to edit (optional)
            
        Returns:
            An instance of the Subscription form
        """
        return RoomieForms.SubscriptionForm(data=data, instance=instance)
    
    def create_review_form(self, data=None, instance=None):
        """
        Creates a form for reviews.
        
        Args:
            data: Form data for binding (optional)
            instance: Review instance to edit (optional)
            
        Returns:
            An instance of the Review form
        """
        return RoomieForms.ReviewForm(data=data, instance=instance)
    
    def create_message_form(self, data=None, instance=None):
        """
        Creates a form for messages.
        
        Args:
            data: Form data for binding (optional)
            instance: Message instance to edit (optional)
            
        Returns:
        
            An instance of the Message form
        """
        return RoomieForms.MessageForm(data=data, instance=instance)