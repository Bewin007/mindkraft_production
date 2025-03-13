from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='registration'),
     path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('forgot-password/', InitiateForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordWithOTPView.as_view(), name='reset-password'),
]