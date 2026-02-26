from celery import shared_task
from django.core.mail import send_mass_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from The_Wow import settings

from .models import Event, EventRegistration

@shared_task(bind=True, autoretry_for=(Exception,), max_retries=3)
def follow_email_to_guests(self, event_id):
    event = Event.objects.get(id=event_id)
    registrations = EventRegistration.objects.select_related('user').filter(
            event=event 
        )
    try:
        email_data = []

        for reg in registrations:
            subject = f"Reminder for {event.title}"
            message = f"Hi {reg.user.name}, \
            This is to remind you that {event.title} is scheduled for \
            Date: {event.date} \
            Time: {event.time} \
            Venue: {event.venue} \
            \
            Please be on time and secure your seat. \
            Thank you! \
            "
            email_data.append((subject, message, settings.EMAIL_HOST_USER, [reg.user.email]))

        if email_data:
            send_mass_mail(email_data, fail_silently=False)

    except Exception as e:
        return HttpResponse("Could not send mail", e)