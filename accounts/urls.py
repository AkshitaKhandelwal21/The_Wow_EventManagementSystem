from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('save_card/', views.SaveCardView.as_view(), name='save_card'),
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/', views.VerifyEmailPageView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationLink.as_view(), name='resend-verification-link'),
    path('verify/<str:token>/', views.SendEmailVerificationView.as_view(), name='email-verification'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset_password/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change-pass'),
    path('profile/', views.ProfilePageView.as_view(), name='profile'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit-profile'),
    path('delete_user/<int:id>', views.DeleteProfileView.as_view(), name='delete-user'),
    path('all_users/', views.AllUsersView.as_view(), name='all_users'),
    path('all_orgs/', views.AllOrganizersView.as_view(), name='all_orgs'),
    path('phone_url/', views.OTPVerificationView.as_view(), name='phone'),
    path('verify_otp', views.VerifyOTP.as_view(), name='verify-otp'),
]
