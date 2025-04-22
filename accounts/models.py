from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone
import random
import string
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, phone, role='CUSTOMER', password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number must be provided")
        
        user = self.model(phone=phone, role=role, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_verified', True)

        return self.create_user(phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    )
    
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_seller(self):
        return self.role == 'SELLER'
    
    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.phone}"
    
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = ''.join(random.choices('0123456789', k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at
    
    def verify(self, otp_input):
        if self.is_valid() and self.otp == otp_input:
            self.is_verified = True
            self.user.is_verified = True
            self.user.save()
            self.save()
            return True
        return False


# accounts/models.py (add OTP model)
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} - OTP Sent"
