from django.contrib import admin

from accounts.models import CustomUser, EmailVerificationToken, PasswordVerificationToken, TimeStamps

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordVerificationToken)