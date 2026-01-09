from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from The_Wow import settings
from accounts.forms import LoginForm, RegistrationForm
from accounts.models import CustomUser
from django.core.mail import send_mail

from accounts.utils import generate_verification_token, send_email

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
            
            user.email_verification_token = generate_verification_token()
            user.email_verification_sent_at = timezone.now()
            user.save()
            send_email(user)
            return HttpResponse("Please verify the email")
        
        return self.render_to_response({'form': form})


class SendEmailVerificationView(TemplateView):
    template_name = 'login.html'
    def get(self, request, *args, **kwargs):
        # context = super().get_context_data(**kwargs)
        token = kwargs.get('token')
        user = CustomUser.objects.filter(email_verification_token=token).first()
        if not user:
            return redirect('signup')
        
        if not user.email_verified:
            user.email_verified = True
            user.save()
            
        return redirect('login')   


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
            return HttpResponse("User Logged In")
        
        return render(request, self.template_name, {'form': LoginForm()})