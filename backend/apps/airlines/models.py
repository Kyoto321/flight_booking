from django.db import models
from django.utils.text import slugify
from apps.common.models import TimeStampedModel


class Airline(TimeStampedModel):
    """
    Master airline record.
    Example:
        Air Peace
        Arik Air
        Ibom Air
        Max Air
        Aero Contractors
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    logo = models.URLField(blank=True)

    priority = models.PositiveIntegerField(default=10, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)
    search_enabled = models.BooleanField(default=True)
    booking_enabled = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["priority", "name"]
        verbose_name = "Airline"
        verbose_name_plural = "Airlines"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)


class Airport(TimeStampedModel):
    """
    Nigerian airports now, scalable internationally later.
    Example:
        LOS - Lagos
        ABV - Abuja
        PHC - Port Harcourt
    """

    name = models.CharField(max_length=120)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")

    iata_code = models.CharField(max_length=3, unique=True, db_index=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_searchable = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["city", "name"]
        verbose_name = "Airport"
        verbose_name_plural = "Airports"

    def __str__(self):
        return f"{self.city} ({self.iata_code})"

    def save(self, *args, **kwargs):
        self.iata_code = self.iata_code.upper().strip()
        super().save(*args, **kwargs)


class Route(TimeStampedModel):
    """
    Airline route map.
    Example:
        Air Peace: LOS -> ABV
    """

    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="routes",
    )

    from_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes",
    )

    to_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes",
    )

    estimated_duration_mins = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional route duration estimate",
    )

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["airline__priority", "from_airport__city"]
        unique_together = ("airline", "from_airport", "to_airport")

        indexes = [
            models.Index(fields=["airline", "from_airport", "to_airport"]),
            models.Index(fields=["from_airport", "to_airport"]),
            models.Index(fields=["is_active"]),
        ]

        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_airport=models.F("to_airport")),
                name="prevent_same_origin_destination",
            )
        ]

        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self):
        return (
            f"{self.airline.code}: "
            f"{self.from_airport.iata_code} -> "
            f"{self.to_airport.iata_code}"
        )


class ProviderHealth(TimeStampedModel):
    """
    Tracks provider / connector health.
    Useful for:
        - search provider monitoring
        - circuit breaker logic
        - admin diagnostics
    """

    class State(models.TextChoices):
        HEALTHY = "HEALTHY", "Healthy"
        FAILING = "FAILING", "Failing"
        RECOVERING = "RECOVERING", "Recovering"
        DISABLED = "DISABLED", "Disabled"

    airline = models.OneToOneField(
        Airline,
        on_delete=models.CASCADE,
        related_name="health",
    )

    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.HEALTHY,
        db_index=True,
    )

    last_checked = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_failure = models.DateTimeField(null=True, blank=True)

    avg_response_ms = models.PositiveIntegerField(default=0)

    failure_count = models.PositiveIntegerField(default=0)
    consecutive_failures = models.PositiveIntegerField(default=0)

    is_healthy = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["airline__priority", "airline__name"]
        verbose_name = "Provider Health"
        verbose_name_plural = "Provider Health"

    def __str__(self):
        return f"{self.airline.name} - {self.state}"