from django.db import models

# Create your models here.
class RoommateProfile(models.Model):
    """
    A Django model representing a roommate profile in the roommate matching platform.

    This model stores essential information about individuals looking for roommates
    or shared accommodations, including their personal details, location preferences,
    and housing requirements.

    Attributes:
        name (CharField): The full name of the person, max length 100 characters.
        city (CharField): The city where the person is looking for accommodation, max length 50 characters.
        area (CharField): The specific area or neighborhood preferred, max length 100 characters.
        budget (IntegerField): The maximum monthly budget in the local currency.
        room_type (CharField): The preferred type of room or accommodation, max length 50 characters.
        image (ImageField): Optional profile picture of the person, stored in 'roommate_images/' directory.
    """
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    budget = models.IntegerField()
    room_type = models.CharField(max_length=50)
    image = models.ImageField(upload_to='roommate_images/', blank=True, null=True)

