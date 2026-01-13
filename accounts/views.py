from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth import authenticate, login, logout
from The_Wow import settings
from django.urls import reverse_lazy
from accounts.forms import ChangePasswordForm, EditProfileForm, ForgotPasswordForm, LoginForm, RegistrationForm, ResetPasswordForm
from accounts.models import CustomUser, EmailVerificationToken, PasswordVerificationToken
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.utils import create_password_verification_token, create_verification_token, send_email, send_pass_reset_mail

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
    

class ForgotPasswordView(TemplateView):
    template_name = 'forgotPassword.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ForgotPasswordForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            print(email)
            user = CustomUser.objects.filter(email=email).first()
            # print(user.email)

            # if not user:
            #     return redirect('signup')
            
            token_obj = create_password_verification_token(user)
            send_pass_reset_mail(user, token_obj.token)
            return HttpResponse("Click on the link to change password")
        
        return self.render_to_response({'form': form})


class ResetPasswordView(TemplateView):
    template_name = 'reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs['token']
        context['form'] = ResetPasswordForm()
        context['token'] = token
        return context

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        token = self.kwargs['token']
        token_obj = PasswordVerificationToken.objects.select_related('user').filter(
            token=token, is_blacklisted=False
        ).first()

        if form.is_valid():
            user = token_obj.user
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            token_obj.is_blacklisted = True
            token_obj.save()

            return redirect('login')
        return self.render_to_response({'form': form})
    

class ChangePasswordView(TemplateView):
    template_name = 'change_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChangePasswordForm(self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        
        return self.render_to_response({'form': form})


class ProfilePageView(TemplateView):
    template_name = 'profile_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = CustomUser.objects.filter(id=self.request.user.id)
        return context
    

class EditProfileView(TemplateView):
    template_name = 'edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        user = get_object_or_404(CustomUser, id=self.kwargs['id'])
        context['form'] = EditProfileForm(instance=user)
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=self.kwargs['id'])
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        
        return self.render_to_response({'form': form, 'user': user})    
    

class DeleteProfileView(LoginRequiredMixin, View):
    model = CustomUser
    # success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=self,kwargs=['id'])
        user.delete()
        return redirect('login')
    

class AllUsersView(TemplateView):
    template_name = 'all_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects.filter(role='user').all()
        context['users'] = users
        return context
    

class AllOrganizersView(TemplateView):
    template_name = "all_organizers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orgs = CustomUser.objects.filter(role='organizer').all()
        context['users'] = orgs
        return context