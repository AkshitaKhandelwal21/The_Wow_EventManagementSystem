from django.db import models

from accounts.models import TimeStamps

# Create your models here.
class Event(TimeStamps, models.Model):
    class Category(models.TextChoices):
        BUSINESS = "Business"
        SOCIAL = "Social"
        ENTERTAINMENT = "Entertainment"
        CULTURAL = "Cultural"
        FOOD = "Food"
        SPORTS = "Sports"
        EDUCATION = "Educational"
        VIRTUAL = "Online"
        TECH = "Technical"
        CHARITY = "Charity"
        OTHERS = "Others"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='events')
    category = models.CharField(max_length=100, choices=Category.choices)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=2)
    address = models.CharField(max_length=500, null=True)
    seats = models.IntegerField(null=True)
    image = models.ImageField(upload_to='events/', blank=True)

    class Meta:
        ordering = ["-date", "-time"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["category"]),
        ]


class EventRegistration(TimeStamps, models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='event_reg')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='registrations')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_event_registration"
            )
        ]


