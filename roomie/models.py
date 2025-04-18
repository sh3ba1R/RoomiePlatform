from django.db import models

# Create your models here.
class RoommateProfile(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    budget = models.IntegerField()
    room_type = models.CharField(max_length=50)
    image = models.ImageField(upload_to='roommate_images/', blank=True, null=True)

