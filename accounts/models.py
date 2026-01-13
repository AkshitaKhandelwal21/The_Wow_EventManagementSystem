from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from accounts.managers import UserManager

# Create your models here.

class TimeStamps(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class CustomUser(AbstractUser, TimeStamps):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin"
        ORGANIZER = "organizer"
        USER = "user"

    class GenderChoices(models.TextChoices):
        MALE = "M"
        FEMALE = "F"
        OTHER = "O"
        PREFER_NOT_TO_SAY = "NA"

    username = None
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=50, choices=RoleChoices, default=RoleChoices.USER)
    profile_photo = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, default=GenderChoices.PREFER_NOT_TO_SAY)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=200, blank=True)
    pin = models.IntegerField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    email_verified = models.BooleanField(default=False)
    # email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    # email_verification_sent_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class EmailVerificationToken(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_blacklisted = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at
    

class PasswordVerificationToken(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_blacklisted = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at
