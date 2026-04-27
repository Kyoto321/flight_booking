from django.db import models
from apps.common.models import TimeStampedModel

class Airline(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    logo = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=10)
    search_enabled = models.BooleanField(default=True)
    booking_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Airport(TimeStampedModel):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=3, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city} ({self.iata_code})"

class Route(TimeStampedModel):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='routes')
    from_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_routes')
    to_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_routes')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('airline', 'from_airport', 'to_airport')

    def __str__(self):
        return f"{self.airline.code}: {self.from_airport.iata_code} -> {self.to_airport.iata_code}"

class ProviderHealth(TimeStampedModel):
    STATE_CHOICES = [
        ('CLOSED', 'Healthy'),
        ('OPEN', 'Failing'),
        ('HALF_OPEN', 'Recovering'),
    ]
    
    airline = models.OneToOneField(Airline, on_delete=models.CASCADE, related_name='health')
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='CLOSED')
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)
    avg_response_ms = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    is_healthy = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.airline.name} Health: {self.state}"
