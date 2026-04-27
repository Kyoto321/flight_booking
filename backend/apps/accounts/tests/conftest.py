import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "phone": "+2348012345678",
        "password": "testpassword123"
    }

@pytest.fixture
def authenticated_client(api_client, user_data):
    user = User.objects.create_user(**user_data)
    api_client.force_authenticate(user=user)
    return api_client, user
