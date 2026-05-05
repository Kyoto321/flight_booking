from django.db.models import Q
from rest_framework import generics, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Airline, Airport, Route, ProviderHealth
from .serializers import (
    AirlineSerializer,
    AirlineDropdownSerializer,
    AirportSerializer,
    AirportDropdownSerializer,
    RouteSerializer,
    ProviderHealthSerializer,
    ProviderHealthSerializer,
)


# ==========================================================
# AIRLINES
# ==========================================================

class AirlineListAPIView(generics.ListAPIView):
    """
    GET /api/v1/airlines/

    Returns active airlines ordered by priority.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AirlineSerializer

    def get_queryset(self):
        return Airline.objects.filter(
            is_active=True
        ).order_by("priority", "name")


class AirlineDropdownAPIView(generics.ListAPIView):
    """
    GET /api/v1/airlines/dropdown/
    Lightweight version for mobile dropdowns.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AirlineDropdownSerializer

    def get_queryset(self):
        return Airline.objects.filter(
            is_active=True
        ).order_by("priority", "name")


# ==========================================================
# AIRPORTS
# ==========================================================

class AirportListAPIView(generics.ListAPIView):
    """
    GET /api/v1/airports/
    Optional:
        ?search=lagos
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AirportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["city", "name", "iata_code", "state"]

    def get_queryset(self):
        return Airport.objects.filter(
            is_active=True,
            is_searchable=True
        ).order_by("city", "name")


class AirportDropdownAPIView(generics.ListAPIView):
    """
    GET /api/v1/airports/dropdown/
    Lightweight version for mobile search fields.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AirportDropdownSerializer

    def get_queryset(self):
        return Airport.objects.filter(
            is_active=True,
            is_searchable=True
        ).order_by("city", "name")


# ==========================================================
# ROUTES
# ==========================================================

class RouteListAPIView(generics.ListAPIView):
    """
    GET /api/v1/routes/

    Optional filters:
        ?from=LOS
        ?to=ABV
        ?airline=P4
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = Route.objects.select_related(
            "airline",
            "from_airport",
            "to_airport"
        ).filter(
            is_active=True,
            airline__is_active=True,
            from_airport__is_searchable=True,
            to_airport__is_searchable=True
        )

        origin = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        airline = self.request.query_params.get("airline")

        if origin:
            queryset = queryset.filter(
                from_airport__iata_code=origin.upper()
            )

        if destination:
            queryset = queryset.filter(
                to_airport__iata_code=destination.upper()
            )

        if airline:
            queryset = queryset.filter(
                airline__code=airline.upper()
            )

        return queryset.order_by(
            "airline__priority",
            "from_airport__city"
        )


# ==========================================================
# PROVIDER HEALTH (ADMIN)
# ==========================================================

class ProviderHealthListAPIView(generics.ListAPIView):
    """
    GET /api/v1/providers/health/

    Should later be admin-only.
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = ProviderHealthSerializer

    def get_queryset(self):
        return ProviderHealth.objects.select_related(
            "airline"
        ).all()
