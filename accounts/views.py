from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth import authenticate, login, logout
from The_Wow import settings
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import ChangePasswordForm, EditProfileForm, ForgotPasswordForm, LoginForm, OTPForm, PhoneNumberForm, RegistrationForm, ResetPasswordForm, CardDetailsForm
from accounts.models import CardModel, CustomUser, EmailVerificationToken, PasswordVerificationToken
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.service import AccountsService
from accounts.tasks import send_email_verification_mail
from accounts.utils import create_password_verification_token, create_verification_token, send_pass_reset_mail

# Create your views here.
class SignupView(TemplateView):
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form1'] = RegistrationForm(prefix='form1')
        context['form2'] = CardDetailsForm(prefix='form2')
        form1_data = CustomUser.objects.all()
        form2_data = CardModel.objects.all()
        context['form1_data'] = form1_data
        context['form2_data'] = form2_data

        return context
    
    def post(self, request, *args, **kwargs):
        form1 = RegistrationForm(request.POST, request.FILES, prefix="form1")
        form2 = CardDetailsForm(request.POST, prefix="form2")
        # user = CustomUser.objects.filter(email=form.email)
        if 'submit_form1' in request.POST:
            if form1.is_valid():
                user = form1.save()
                user.save()
                token_obj = create_verification_token(user)

                request.session['email'] = user.email
                send_email_verification_mail.delay(user.name, user.email, token_obj.token)
                # return redirect('verify-email')
                return redirect('save_card')
            
        return render(request, 'register.html', {
            'form1': form1
        })
    

class SaveCardView(TemplateView):
    template_name = 'save_card.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form2'] = CardDetailsForm()
        return context

    def post(self, request, *args, **kwargs):
        form2 = CardDetailsForm(request.POST)
        if form2.is_valid():
            card_number = form2.cleaned_data['card_number']
            card = form2.save(commit=False)
            sha_hash = AccountsService.sha_hash256(self, card_number)
            django_hash_value = AccountsService.django_hash(self, card_number)
            card.card_number_hash = sha_hash
            card.card_number_django_hash = django_hash_value
            card.last4 = card_number[-4:]
            card.save()
            return redirect('verify-email')
        
        return render(request, self.template_name, {'form2': form2})
    

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
            send_email_verification_mail(user.name, user.email, token_obj.token)
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
            
        messages.error(request, "Invalid username or password")        
        return render(request, self.template_name, {'form': LoginForm()})
    

class OTPVerificationView(TemplateView):
    template_name = 'phone_num.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PhoneNumberForm()
        return context
    
    def post(self, request, *args, **kwargs):
        phone = request.POST.get('phone')
        user = CustomUser.objects.filter(phone=phone).first()
        if not user:
            messages.error(request, "Phone number not registered")
            return redirect('login')
        otp = AccountsService.send_OTP(phone)
        request.session['otp'] = otp
        request.session['phone'] = phone
        return redirect('verify-otp')
        
        
class VerifyOTP(TemplateView):
    template_name = 'get_otp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = OTPForm()
        return context
    
    def post(self, request, *args, **kwargs):
        input_otp = request.POST.get('otp')
        otp = request.session.get('otp')
        phone = request.session.get('phone')

        if str(input_otp) == str(otp):
            user = CustomUser.objects.get(phone=phone)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session.pop('otp')
            request.session.pop('phone')
            return redirect('profile')
    

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
        context['user'] = self.request.user
        return context
    

class EditProfileView(TemplateView):
    template_name = 'edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        # user = get_object_or_404(CustomUser, id=self.kwargs['id'])
        context['form'] = EditProfileForm(instance=self.request.user)
        # context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        # user = get_object_or_404(CustomUser, id=self.kwargs['id'])
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        
        return self.render_to_response({'form': form})    
    

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