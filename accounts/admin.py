from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import CustomUser, EmailVerificationToken, PasswordVerificationToken, TimeStamps

class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'name', 'phone', 'role'
    ]
    list_filter = ['is_staff']

    fieldsets = [
        ("User Credentials", {'fields': [
            'email', 'password'
        ]}),
        ("Personal Information", {'fields': [
            'phone', 'gender', 'role', 'city', 'state', 'bio', 'email_verified'
        ]}),
        ("Permissions", {"fields": [
            "is_staff",
            "is_superuser",
            "is_active",
            "groups",
            "user_permissions"
            ]}),
    ]
    search_fields = ["email"]
    ordering = ["email"]

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordVerificationToken)