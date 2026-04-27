from django.db import models
from apps.common.models import TimeStampedModel
from fernet_fields import EncryptedCharField

class Passenger(TimeStampedModel):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    PASSENGER_TYPE_CHOICES = [
        ('ADULT', 'Adult'),
        ('CHILD', 'Child'),
        ('INFANT', 'Infant'),
    ]
    RELATIONSHIP_CHOICES = [
        ('SELF', 'Self'),
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('FRIEND', 'Friend'),
        ('STAFF', 'Staff'),
        ('OTHER', 'Other'),
    ]
    ID_TYPE_CHOICES = [
        ('PASSPORT', 'Passport'),
        ('NIN', 'NIN'),
        ('VOTERS', 'Voters Card'),
    ]

    owner = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='passengers'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, default='Nigerian')
    passenger_type = models.CharField(max_length=10, choices=PASSENGER_TYPE_CHOICES)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES)
    id_number = EncryptedCharField(max_length=100) # Encrypted at rest
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.passenger_type})"
