from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CardModel, CustomUser
from django.contrib.auth.forms import PasswordChangeForm

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Enter password again'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'password1', 'password2', 'role', 'profile_photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your sweet name'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Eg: hello@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'phone',
                'placeholder': 'Enter your phone number'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class CardDetailsForm(forms.ModelForm):
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    class Meta:
        model = CardModel
        fields = ['card_number', 'card_holder', 'expiration']
        widgets = {
            'card_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'card_holder': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'expiration': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    widgets = {
        'email': forms.TextInput(attrs={
            'class': 'form-control'
        }),
        'password': forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    }


class PhoneNumberForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput)
    widgets = {
    'phone': forms.TextInput(attrs={
        'class': 'form-control'
    }),
    }


class OTPForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput)
    widgets = {
    'otp': forms.TextInput(attrs={
        'class': 'form-control'
    }),
    }


class ForgotPasswordForm(forms.Form):
    email = forms.CharField()
    widgets = {
        'email': forms.TextInput(attrs={
            'class': 'form-control'
        })
    }
    

class ResetPasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control'
            })
        }


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField()
    new_password = forms.CharField()
    confirm_password = forms.CharField()
    widgets = {
        'old_password': forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        'new_password': forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a new password'
        }),
        'confirm_password': forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the same password again'
        })
    }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_photo', 'name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your sweet name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            })
        }