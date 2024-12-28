from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'  # Add namespace

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('forgot-password/', views.CustomPasswordResetView.as_view(), name='forgot_password'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]