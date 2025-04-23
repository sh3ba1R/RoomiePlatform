from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone



# The modles we need
#  1- User with the attributes (1-ID/key 2-status 3-user type(seeker or providor 4-PhoneNumber 5-password 6-email 7-profile pic 8-name )
#  2- Room (1-ID/key 2-title 3-location 4-description 5-price 6-availability 7-rating 8-reviews 9- Owner )
#  3- contract (1-ID/key 2-create date 3-status 4-rent amount 5-start date 6-end date)
#  4- message (1- ID/key 2-sender 3-reciever 4-content 5-is read)
#  5- review (1- ID/key 2-writer 3-room 4-contract id 5-rating 6-comment 7-time)
#  6- subscription (1-ID/key 2-userID 3-plan 4-status 5-startDate 6-endDate 7- price)
#  7- support ticket (1- ID/key 2- user id 3-description 4-create date 5-status 6-subject )
#  8- Admin (1-ID/key 2-email 3- password 4-role )
#  9- matching roommate (1- room ID 2- status 3-date 4-contract 5- as many users )
# Create your models here.

class User(AbstractUser):
    ACCOUNT_TYPE_CHOICES = [
        ('seeker', 'Seeker'),
        ('provider', 'Provider'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='seeker')

    def __str__(self):
        return self.username

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)  # Custom primary key
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits=8, decimal_places=2)
    room_type = models.CharField(max_length=20, choices=[
        ('private', 'Private Room'),
        ('shared', 'Shared Room'),
        ('studio', 'Studio'),
        ('apartment', 'Apartment'),
    ])
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location}"

# Optional: Track interest in a room
class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.seeker.username} for {self.room.title} ({self.status})"

class RoomContract(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='contracts')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_contracts')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provided_contracts')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Contract for {self.room.title} between {self.seeker.username} and {self.provider.username}"

    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.title} by {self.user.username} - {self.status}"
    

class Subscription(models.Model):
    """
    Represents a user subscription in the system.
    This model tracks subscription details for users, including their plan type,
    start and end dates, and active status.
    Attributes:
        user (OneToOneField): Link to the User model with cascade deletion.
        plan (CharField): Subscription plan type - 'free', 'monthly', or 'yearly'.
        start_date (DateField): When the subscription began (auto-set on creation).
        end_date (DateField): When the subscription ends (optional).
        is_active (BooleanField): Whether the subscription is currently active.
    Methods:
        __str__: Returns a string representation of the subscription.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"    
    

class RoomReview(models.Model):

    booking = models.OneToOneField(RoomBooking, on_delete=models.CASCADE, related_name='review')  # Link review to booking
    rating = models.PositiveIntegerField(default=1, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.room.title} by {self.booking.seeker.username} ({self.rating}/5)"
    
    def save(self, *args, **kwargs):
        if self.booking.status != 'approved':
            raise ValueError("You can only review a room after your booking has been approved")
        super().save(*args, **kwargs)

class UserReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')  # User giving the review
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')  # User being rated
    rating = models.PositiveIntegerField(default=1, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username} ({self.rating}/5)"

# Message Model
class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}: {self.subject}"