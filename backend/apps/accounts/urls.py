from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, VerifyOTPView, ResendOTPView, ProfileView, LoginView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp-verify'),
    path('otp/resend/', ResendOTPView.as_view(), name='otp-resend'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
