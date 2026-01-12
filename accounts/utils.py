import uuid
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from The_Wow import settings
from accounts.models import EmailVerificationToken, PasswordVerificationToken


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


def create_password_verification_token(user):
    PasswordVerificationToken.objects.filter(
         user=user, is_blacklisted=False
    ).update(is_blacklisted=True)

    token_obj = PasswordVerificationToken.objects.create(
         user=user, token=uuid.uuid4().hex,
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
        

def send_pass_reset_mail(user, token):
     verify_url = f'http://127.0.0.1:9000/reset_password/{token}'
     try:
          subject = 'Reset your password'
          message = f"Hi {user.name}, Click the link below to reset your password \
          \
          {verify_url} \
          "
          recipient = [user.email]
          send_mail(subject, message, settings.EMAIL_HOST_USER, recipient)
     except Exception as e:
          raise e