import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Passenger

User = get_user_model()

@pytest.mark.django_db
class TestPassengerAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.passenger_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '1990-01-01',
            'gender': 'MALE',
            'nationality': 'Nigerian',
            'passenger_type': 'ADULT',
            'relationship': 'SELF',
            'id_type': 'PASSPORT',
            'id_number': 'A12345678'
        }

    def test_create_passenger(self):
        """Test creating a new passenger"""
        url = reverse('passenger-list')
        response = self.client.post(url, self.passenger_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Passenger.objects.count(), 1)
        passenger = Passenger.objects.first()
        self.assertEqual(passenger.first_name, 'John')
        self.assertEqual(passenger.owner, self.user)

    def test_list_passengers(self):
        """Test listing passengers for authenticated user"""
        # Create a passenger
        Passenger.objects.create(owner=self.user, **self.passenger_data)

        url = reverse('passenger-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_passenger_isolation(self):
        """Test that users can only see their own passengers"""
        # Create another user and their passenger
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        Passenger.objects.create(owner=other_user, **self.passenger_data)

        # Create passenger for current user
        Passenger.objects.create(owner=self.user, **self.passenger_data)

        url = reverse('passenger-list')
        response = self.client.get(url)

        # Should only see 1 passenger (their own)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_passenger(self):
        """Test retrieving a specific passenger"""
        passenger = Passenger.objects.create(owner=self.user, **self.passenger_data)

        url = reverse('passenger-detail', kwargs={'pk': passenger.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')

    def test_update_passenger(self):
        """Test updating a passenger"""
        passenger = Passenger.objects.create(owner=self.user, **self.passenger_data)

        update_data = self.passenger_data.copy()
        update_data['first_name'] = 'Jane'

        url = reverse('passenger-detail', kwargs={'pk': passenger.pk})
        response = self.client.put(url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        passenger.refresh_from_db()
        self.assertEqual(passenger.first_name, 'Jane')

    def test_delete_passenger(self):
        """Test soft deleting a passenger"""
        passenger = Passenger.objects.create(owner=self.user, **self.passenger_data)

        url = reverse('passenger-detail', kwargs={'pk': passenger.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        passenger.refresh_from_db()
        self.assertFalse(passenger.is_active)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access passenger endpoints"""
        self.client.force_authenticate(user=None)

        url = reverse('passenger-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_data(self):
        """Test validation with invalid data"""
        invalid_data = self.passenger_data.copy()
        invalid_data['gender'] = 'INVALID'

        url = reverse('passenger-list')
        response = self.client.post(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data)

    def test_passenger_choices(self):
        """Test that choice fields work correctly"""
        # Test valid choices
        valid_data = self.passenger_data.copy()
        valid_data.update({
            'gender': 'FEMALE',
            'passenger_type': 'CHILD',
            'relationship': 'CHILD',
            'id_type': 'NIN'
        })

        url = reverse('passenger-list')
        response = self.client.post(url, valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
