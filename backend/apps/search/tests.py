from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from apps.airlines.models import Airport

class FlightSearchTests(APITestCase):
    def setUp(self):
        # Create test airports
        self.origin = Airport.objects.create(
            iata_code="LOS",
            city="Lagos",
            name="Murtala Muhammed International",
            is_active=True,
            is_searchable=True
        )
        self.destination = Airport.objects.create(
            iata_code="ABV",
            city="Abuja",
            name="Nnamdi Azikiwe International",
            is_active=True,
            is_searchable=True
        )
        self.search_url = "/api/v1/flights/search/"

    @patch('apps.search.providers.airpeace.AirPeaceProvider.search')
    def test_flight_search_success(self, mock_search):
        # Mocking the provider response
        mock_search.return_value = [{
            "provider": "airpeace",
            "airline": "Air Peace",
            "flight_number": "P47123",
            "origin": "LOS",
            "destination": "ABV",
            "departure_time": "08:00",
            "arrival_time": "09:10",
            "price": 75000.0,
            "currency": "NGN"
        }]

        payload = {
            "origin": "LOS",
            "destination": "ABV",
            "travel_date": "2026-05-13",
            "adults": 1
        }

        response = self.client.post(self.search_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["flight_number"], "P47123")

    def test_search_same_origin_destination(self):
        payload = {
            "origin": "LOS",
            "destination": "LOS",
            "travel_date": "2026-05-13",
            "adults": 1
        }
        response = self.client.post(self.search_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_invalid_airport(self):
        payload = {
            "origin": "LOS",
            "destination": "XYZ",
            "travel_date": "2026-05-13",
            "adults": 1
        }
        response = self.client.post(self.search_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)