from rest_framework import serializers
from .models import Airline, Airport, Route, ProviderHealth


class AirlineSerializer(serializers.ModelSerializer):
    """
    Public airline serializer
    Used for:
        GET /api/v1/airlines/
    """

    class Meta:
        model = Airline
        fields = [
            "id",
            "name",
            "slug",
            "code",
            "logo",
            "priority",
            "is_active",
            "search_enabled",
            "booking_enabled",
        ]
        read_only_fields = fields


class AirlineDropdownSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for dropdowns / search filters
    """

    class Meta:
        model = Airline
        fields = [
            "id",
            "name",
            "code",
            "logo",
        ]
        read_only_fields = fields


class AirportSerializer(serializers.ModelSerializer):
    """
    Full airport serializer
    Used for:
        GET /api/v1/airports/
    """

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "city",
            "state",
            "country",
            "iata_code",
            "display_name",
            "is_active",
        ]
        read_only_fields = fields

    def get_display_name(self, obj):
        return f"{obj.city} ({obj.iata_code})"


class AirportDropdownSerializer(serializers.ModelSerializer):
    """
    Lightweight airport serializer
    Best for mobile search dropdowns
    """

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = [
            "id",
            "iata_code",
            "display_name",
        ]
        read_only_fields = fields

    def get_display_name(self, obj):
        return f"{obj.city} ({obj.iata_code})"


class RouteSerializer(serializers.ModelSerializer):
    """
    Full route serializer
    Mostly internal/admin use
    """

    airline = AirlineDropdownSerializer(read_only=True)
    from_airport = AirportDropdownSerializer(read_only=True)
    to_airport = AirportDropdownSerializer(read_only=True)

    class Meta:
        model = Route
        fields = [
            "id",
            "airline",
            "from_airport",
            "to_airport",
            "estimated_duration_mins",
            "is_active",
        ]
        read_only_fields = fields


class ProviderHealthSerializer(serializers.ModelSerializer):
    """
    Admin / monitoring serializer
    """

    airline = AirlineDropdownSerializer(read_only=True)

    class Meta:
        model = ProviderHealth
        fields = [
            "id",
            "airline",
            "state",
            "last_checked",
            "last_success",
            "last_failure",
            "avg_response_ms",
            "failure_count",
            "consecutive_failures",
            "is_healthy",
        ]
        read_only_fields = fields

