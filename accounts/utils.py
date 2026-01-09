import uuid
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from The_Wow import settings
from accounts.models import EmailVerificationToken


def create_verification_token(user):
     
    EmailVerificationToken.objects.filter(
          user = user, is_blacklisted=False
     ).update(is_blacklisted=True)

    token_obj = EmailVerificationToken.objects.create(
         user=user, 
         token=uuid.uuid4().hex, 
         expires_at=timezone.now() + timedelta(int(settings.TOKEN_EXPIRY_HOURS))
    )

    return token_obj


def send_email(user, token):
        verify_url = f'http://127.0.0.1:9000/verify/{token}'
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