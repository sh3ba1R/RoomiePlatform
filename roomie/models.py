from django.db import models
from django.conf import settings
import uuid
from core.models import Room  # Import Room from core app

# Create your models here.

class Review(models.Model):
    REVIEW_TYPES = (
        ('room', 'Room Review'),
        ('provider', 'Provider Review'),
        ('seeker', 'Seeker Review'),
    )
    
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received', null=True, blank=True)
    reviewed_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track when a review is edited
    
    class Meta:
        ordering = ['-created_at']
        # Ensure a user can only review a room or another user once
        constraints = [
            models.UniqueConstraint(
                fields=['reviewer', 'reviewed_room'],
                condition=models.Q(reviewed_room__isnull=False),
                name='unique_room_review'
            ),
            models.UniqueConstraint(
                fields=['reviewer', 'reviewed_user'],
                condition=models.Q(reviewed_user__isnull=False),
                name='unique_user_review'
            )
        ]
    
    def __str__(self):
        if self.review_type == 'room':
            return f"Review for {self.reviewed_room.title} by {self.reviewer.username}"
        else:
            return f"Review for {self.reviewed_user.username} by {self.reviewer.username}"
    
    def get_absolute_url(self):
        """Return the URL for viewing this review."""
        if self.review_type == 'room':
            return f"/room/{self.reviewed_room.room_id}#review-{self.review_id}"
        else:
            return f"/user/{self.reviewed_user.id}#review-{self.review_id}"


class ReviewReply(models.Model):
    """Model for storing replies to reviews."""
    reply_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='reply')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Review Replies'

    def __str__(self):
        return f"Reply to review {self.review.review_id} by {self.author.username}"


