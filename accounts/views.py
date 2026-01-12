from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login, logout
from The_Wow import settings
from accounts.forms import LoginForm, RegistrationForm
from accounts.models import CustomUser, EmailVerificationToken
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.utils import create_verification_token, send_email

# Create your views here.
class SignupView(TemplateView):
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST, request.FILES)
        # user = CustomUser.objects.filter(email=form.email)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            token_obj = create_verification_token(user)
            # user.email_verification_token = create_verification_token(user)
            # user.email_verification_sent_at = timezone.now()
            # user.save()
            request.session['email'] = user.email
            send_email(user, token_obj.token)
            return redirect('verify-email')
        
        return self.render_to_response({'form': form})


class VerifyEmailPageView(TemplateView):
    template_name = 'verify_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('email')
        return context


class SendEmailVerificationView(TemplateView):
    template_name = 'login.html'
    def get(self, request, *args, **kwargs):
        # context = super().get_context_data(**kwargs)
        token = kwargs.get('token')

        token_obj = EmailVerificationToken.objects.select_related('user').filter(
            token=token, 
            is_blacklisted=False
        ).first()

        if not token_obj:
            return HttpResponse("Invalid token")
        
        user = token_obj.user

        if not user.email_verified:
            user.email_verified = True
            user.save()
            
        return redirect('login')   


class ResendVerificationLink(TemplateView):
    template_name = 'verify_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('email')
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.session.get('email')
        user = CustomUser.objects.filter(email=email).first()
        print("User: ", user)
        if not user:
            return redirect('signup')
        
        if not user.email_verified:
            print("verifying email")
            token_obj = create_verification_token(user)
            send_email(user, token_obj.token)
            return redirect('verify-email')
        
        return redirect('signup')


class LoginView(TemplateView):  
    # form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return redirect('signup')
        if user and not password:
            return render(request, self.template_name)
        if not user.email_verified:
            return HttpResponse("Please verify your email")

        user_login = authenticate(request, email=email, password=password)
        if user_login:
            login(request, user_login)
            if user.role=="admin":
                return redirect('admin_dashboard')
            elif user.role=="user":
                return redirect('user-dashboard')
            elif user.role=="organizer":
                return redirect('org-dashboard')
        
        return render(request, self.template_name, {'form': LoginForm()})
    

class LogoutView(LoginRequiredMixin ,TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
    