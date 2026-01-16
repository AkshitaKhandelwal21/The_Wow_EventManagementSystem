import hashlib
import random
from django.contrib.auth.hashers import make_password
from twilio.rest import Client
from The_Wow import settings

class AccountsService():

    def sha_hash256(self, card_number):
        return hashlib.sha256(card_number.encode()).hexdigest()
    
    def django_hash(self, card_number):
        return make_password(card_number)
    
    def send_OTP(phone):
     client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
     otp = str(random.randint(10000, 99999))
     client.messages.create(
          body=f"Your otp is {otp}. Please do share it with anyone",
          from_='+1 762 372 7017',
          to='+91' + phone
     )
     return otp
