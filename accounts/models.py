# This is a simple user model for demonstraion purposes
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name=models.CharField(max_length=255,blank=True,null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(
        max_length=50, choices=(("admin", "Admin"), ("user", "User")), default="user"
    )
    is_active = models.BooleanField(default=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username
