from django.db import models

from corebot.utils import upload_location


class User(models.Model):
    chat_id = models.CharField(max_length=255)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)


class Place(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(null=True, blank=True, max_length=150)
    image = models.ImageField(
        upload_to=upload_location,
        null=True,
        blank=True
    )
    latitude = models.FloatField(default=None)
    longitude = models.FloatField(default=None)
