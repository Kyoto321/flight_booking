from rest_framework import serializers
from apps.airlines.models import Airport


class FlightSearchRequestSerializer(serializers.Serializer):

    origin = serializers.CharField(max_length=3)
    destination = serializers.CharField(max_length=3)
    travel_date = serializers.DateField()

    adults = serializers.IntegerField(min_value=1, max_value=9, default=1)
    children = serializers.IntegerField(min_value=0, max_value=9, default=0)
    infants = serializers.IntegerField(min_value=0, max_value=9, default=0)

    preferred_airline = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True
    )

    # -------------------------
    # FIELD VALIDATION
    # -------------------------

    def validate_origin(self, value):
        value = value.upper().strip()

        if not Airport.objects.filter(
            iata_code=value,
            is_active=True,
            is_searchable=True
        ).exists():
            raise serializers.ValidationError("Invalid origin airport")

        return value

    def validate_destination(self, value):
        value = value.upper().strip()

        if not Airport.objects.filter(
            iata_code=value,
            is_active=True,
            is_searchable=True
        ).exists():
            raise serializers.ValidationError("Invalid destination airport")

        return value

    def validate_preferred_airline(self, value):
        return value.upper().strip()

    # -------------------------
    # OBJECT VALIDATION
    # -------------------------

    def validate(self, attrs):
        if attrs["origin"] == attrs["destination"]:
            raise serializers.ValidationError(
                "Origin and destination cannot be the same."
            )

        if attrs["infants"] > attrs["adults"]:
            raise serializers.ValidationError(
                "Each infant must be accompanied by an adult."
            )

        return attrs

    # -------------------------
    # INTERNAL MAPPING
    # -------------------------

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        validated["date"] = validated["travel_date"]
        return validated