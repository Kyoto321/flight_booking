from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, VerifyOTPView, ResendOTPView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp-verify'),
    path('otp/resend/', ResendOTPView.as_view(), name='otp-resend'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
