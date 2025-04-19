from django import forms
from core.models import Room, RoommateProfile, RoomBooking, RoomContract, SupportTicket,Subscription, Review
from message.models import Message


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
        """
        Meta configuration for the Room form.

        This inner class specifies the model and fields to be used in the form.
        It links the form to the Room model and selects specific fields to be included.
        It also customizes the available_from field to use a date input widget.

        Attributes:
            model: The Room model that this form is associated with.
            fields: The fields from the Room model to include in the form.
            widgets: Custom widget definitions for specific form fields.
                available_from: Uses a date input widget for better date selection.
        """
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

    Attributes:
        Meta: Contains metadata about the form, including the associated model,
              fields to include, and widget customizations.
    """
    class Meta:
        """
        Meta configuration for the RoommateProfile form.

        This inner class provides configuration metadata for the form class.

        Attributes:
            model: The RoommateProfile model this form is associated with.
            fields: List of model fields to include in the form.
            widgets: Custom widget configurations for specific fields.
                - bio: Rendered as a textarea with 4 rows instead of the default input.
        """
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