import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.accounts.models import OTPToken

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:
    def test_registration_success(self, api_client, user_data):
        url = reverse('register')
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data['email']).exists()
        assert OTPToken.objects.filter(user__email=user_data['email'], purpose='REGISTER').exists()

    def test_otp_verification_success(self, api_client, user_data):
        # Register first
        api_client.post(reverse('register'), user_data)
        user = User.objects.get(email=user_data['email'])
        otp = OTPToken.objects.get(user=user, purpose='REGISTER')
        
        url = reverse('otp-verify')
        data = {
            "email": user_data['email'],
            "code": otp.code,
            "purpose": "REGISTER"
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        user.refresh_from_db()
        assert user.is_phone_verified is True
