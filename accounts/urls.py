from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/', views.VerifyEmailPageView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationLink.as_view(), name='resend-verification-link'),
    path('verify/<str:token>/', views.SendEmailVerificationView.as_view(), name='email-verification'),
]
