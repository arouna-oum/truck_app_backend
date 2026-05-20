from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)
    google_picture_url = models.URLField(blank=True, null=True)