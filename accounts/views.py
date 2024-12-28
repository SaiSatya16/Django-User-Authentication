from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import SignUpForm, CustomAuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from .forms import ProfileUpdateForm
from django.utils import timezone

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('banking:wallet_dashboard')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('banking:wallet_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('login')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def profile_view(request):
    try:
        if request.method == 'POST':
            form = ProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = ProfileUpdateForm(instance=request.user)
        
        
        
        context = {
            'form': form,
            'user': request.user,
            'account_age': (timezone.now() - request.user.date_joined).days
        }
        return render(request, 'accounts/profile.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return redirect('accounts:dashboard')