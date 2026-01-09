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

    username = None
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=50, choices=RoleChoices, default=RoleChoices.USER)
    profile_photo = models.ImageField(upload_to='profile_pictures', blank=True, null=True)

    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()