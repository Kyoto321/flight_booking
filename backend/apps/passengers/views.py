from rest_framework import viewsets, permissions
from .models import Passenger
from .serializers import PassengerSerializer

class PassengerViewSet(viewsets.ModelViewSet):
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return passengers owned by the current user
        return Passenger.objects.filter(owner=self.request.user, is_active=True)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the owner
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete by setting is_active to False
        instance.is_active = False
        instance.save()
