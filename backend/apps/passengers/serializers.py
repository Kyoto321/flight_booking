from rest_framework import serializers
from .models import Passenger

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = [
            'id', 'first_name', 'last_name', 'dob', 'gender',
            'nationality', 'passenger_type', 'relationship',
            'id_type', 'id_number', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # owner is automatically set to the request user by the view's perform_create
        return super().create(validated_data)
