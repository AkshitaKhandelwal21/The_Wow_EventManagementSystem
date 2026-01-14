from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        if sociallogin.account.provider == "google":
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            user.email_verified = True
            if not full_name:
                user.name = user.email
            user.name = full_name
            user.save(update_fields=['email_verified', 'name'])

        return user