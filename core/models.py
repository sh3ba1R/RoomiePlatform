from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Room(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    rent = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location}"

class RoommateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    preferred_location = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    gender = models.CharField(max_length=20, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])
    is_smoker = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Optional: Track interest in a room
class RoomBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} interested in {self.room.title}"
    

class RoomContract(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    agreement_text = models.TextField()
    signed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract for {self.room.title} with {self.tenant.username}"
    

class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ], default='open')

    def __str__(self):
        return f"{self.subject} ({self.status})"
    

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
    

class Review(models.Model):
    reviewer = models.ForeignKey(User, related_name='given_reviews', on_delete=models.CASCADE)
    reviewee = models.ForeignKey(User, related_name='received_reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"


