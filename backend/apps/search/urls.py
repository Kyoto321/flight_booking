# apps/search/urls.py
from django.urls import path
from .views import FlightSearchAPIView

urlpatterns = [
    path("flights/search/", FlightSearchAPIView.as_view()),
]