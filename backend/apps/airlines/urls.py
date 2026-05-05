from django.urls import path
from .views import (
    AirlineListAPIView,
    AirlineDropdownAPIView,
    AirportListAPIView,
    AirportDropdownAPIView,
    RouteListAPIView,
    ProviderHealthListAPIView,
)

urlpatterns = [
    path("airlines/", AirlineListAPIView.as_view()),
    path("airlines/dropdown/", AirlineDropdownAPIView.as_view()),

    path("airports/", AirportListAPIView.as_view()),
    path("airports/dropdown/", AirportDropdownAPIView.as_view()),

    path("routes/", RouteListAPIView.as_view()),

    path("providers/health/", ProviderHealthListAPIView.as_view()),
]