import uuid
from django.core.mail import send_mail
from The_Wow import settings


def generate_verification_token():
    return str(uuid.uuid4())

def send_email(user):
        verify_url = f'http://127.0.0.1:9000/verify/{user.email_verification_token}'
        try:
            subject = "Verify your account"
            message = f"Hi {user.name}, thank you for registering in The-Wow. \
            Click on the link to verify \
            {verify_url} \
            "
            receipent = [user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, receipent)
        
        except Exception as e:
            raise e