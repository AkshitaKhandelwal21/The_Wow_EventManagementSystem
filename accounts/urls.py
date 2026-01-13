from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/', views.VerifyEmailPageView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationLink.as_view(), name='resend-verification-link'),
    path('verify/<str:token>/', views.SendEmailVerificationView.as_view(), name='email-verification'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset_password/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', views.ProfilePageView.as_view(), name='profile'),
    path('edit_profile/<int:id>/', views.EditProfileView.as_view(), name='edit-profile'),
]
