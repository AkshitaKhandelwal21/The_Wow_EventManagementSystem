from celery import shared_task
from django.core.mail import send_mail
from The_Wow import settings

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={
    'max_retries': 3, 'countdown': 5})
def send_email_verification_mail(self, user_name, user_email, token):
    verify_url = f'http://127.0.0.1:9000/verify/{token}'
    try:
        subject = "Verify your account"
        message = f"Hi {user_name}, thank you for registering in The-Wow. \
        Click on the link to verify \
        {verify_url} \
        "
        receipent = [user_email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, receipent)
    
    except Exception as e:
        raise e

