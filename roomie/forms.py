from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from core.models import Room, User, RoomBooking, RoomContract, SupportTicket, Subscription, Message
from roomie.models import Review, ReviewReply

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
            - RoomID
            - provider
            - title: Title of the room listing
            - description: Detailed description of the room
            - location: Geographic location of the room
            - price: Monthly rent price
            - roomType
            - Is available: Date when the room becomes available
            - created at

        Widgets:
            - available_from: Uses a date input widget for better date selection
        """
        class Meta:
            model = Room
            fields = ['provider', 'title', 'description', 'location', 'rent', 'room_type','bedrooms', 'is_available', 'image']
            exclude = ['provider']  # Exclude the provider field from the form
            widgets = {
                'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            }


    class UserForm(UserCreationForm):
        """
        Custom user registration form extending UserCreationForm.
        Includes additional fields for gender, birthdate, bio, location, profile photo, and account type.
        """
        class Meta:
            model = User
            fields = ['username', 'email', 'gender', 'birthdate', 'bio', 'location', 'profile_photo', 'account_type']
            widgets = {
                'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
                'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
                'account_type': forms.Select(attrs={'class': 'form-control'}),
        }
            
    class UserProfileForm(forms.ModelForm):
        """
        Form for creating or updating a roommate profile.

        This form is linked to the RoommateProfile model and includes fields
        for basic personal information such as age, gender, occupation, and bio.
        The bio field is rendered as a text area with 4 rows for better user experience.
        """
        email = forms.EmailField(required=True)
        class Meta:
            model = User
            fields = ['username', 'email', 'gender', 'birthdate', 'bio', 'location', 'profile_photo', 'account_type']

    class RoomBookingForm(forms.ModelForm):
        """
        Form for booking rooms.
        
        Allows users to select a room and specify the booking period.
        """
        class Meta:
            model = RoomBooking
            fields = ['start_date', 'end_date']  # Only include fields relevant to seekers
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    class RoomContractForm(forms.ModelForm):
        """
        Form for creating room rental contracts.
        
        Allows creation of legally binding contracts between users and room owners.
        """
        class Meta:
            model = RoomContract
            fields = ['room', 'seeker', 'provider', 'start_date', 'end_date', 'rent_amount', 'status']


    class SupportTicketForm(forms.ModelForm):
        """
        Form for creating support tickets.
        
        Allows users to report issues or request assistance.
        """
        class Meta:
            model = SupportTicket
            fields = ['title', 'description']
            widgets = {
                'title': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter a title for your support ticket'
                }),
                'description': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': 'Describe your issue in detail...'
                }),
            }


    class SubscriptionForm(forms.ModelForm):
        """
        Form for managing subscription plans.
        
        Allows users to select a subscription plan and payment method.
        """
        class Meta:
            model = Subscription
            fields = ['user', 'plan', 'end_date', 'is_active']

    class ReviewForm(forms.ModelForm):
        """
        Form for submitting reviews for rooms or users.
        """
        comment = forms.CharField(
            widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience... What did you like or dislike?'
            }),
            required=True
        )
        
        class Meta:
            model = Review
            fields = ['rating', 'comment']
            widgets = {
                'rating': forms.RadioSelect(attrs={'class': 'rating-input'})
            }
            
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['rating'].required = True
            self.fields['rating'].label = "Your Rating"
            self.fields['comment'].label = "Your Review"

    class ReviewReplyForm(forms.ModelForm):
        """
        Form for replying to reviews.
        """
        content = forms.CharField(
            widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your response to this review...'
            }),
            required=True
        )
        
        class Meta:
            model = ReviewReply
            fields = ['content']
            
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['content'].label = "Your Response"

    class MessageForm(forms.ModelForm):
        """
        Form for sending messages to other users.
        """
        class Meta:
            model = Message
            fields = ['subject', 'body']
            widgets = {
                'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
                'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message here...'}),
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
        return RoomieForms.UserForm(data=data, instance=instance)
    
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
        Creates a form for submitting reviews.
        
        Args:
            data: Form data for binding (optional)
            instance: Review instance to edit (optional)
            
        Returns:
            An instance of the Review form
        """
        return RoomieForms.ReviewForm(data=data, instance=instance)
    
    def create_review_reply_form(self, data=None, instance=None):
        """
        Creates a form for replying to reviews.
        
        Args:
            data: Form data for binding (optional)
            instance: ReviewReply instance to edit (optional)
            
        Returns:
            An instance of the ReviewReply form
        """
        return RoomieForms.ReviewReplyForm(data=data, instance=instance)