from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from accounts.forms import LoginForm, RegistrationForm
from accounts.models import CustomUser

# Create your views here.
class SignupView(TemplateView):
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
        
        return self.render_to_response({'form': form})


class LoginView(TemplateView):
    # form_class = LoginForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context
    
    # def get(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return HttpResponse("Logged In")
    #     return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return redirect('signup')
        
        user_login = authenticate(email=email, password=password)
        if user_login:
            login(request, user_login)
            return HttpResponse("User Logged In")