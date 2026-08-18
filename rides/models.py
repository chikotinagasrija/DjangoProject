import uuid
from django.db import models
from django.conf import settings

class VehicleType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class DriverProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )

    license_number = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)

class DriverLocation(models.Model):

    class AvailabilityStatus(models.TextChoices):
        ONLINE = "ONLINE", "Online"
        OFFLINE = "OFFLINE", "Offline"
        BUSY = "BUSY", "Busy"

    driver = models.OneToOneField(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name="location"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    last_updated = models.DateTimeField(auto_now=True)

    availability_status = models.CharField(
        max_length=10,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.OFFLINE
    )
    class Meta:
       indexes = [
        models.Index(
            fields=["availability_status"]
        ),
    ]

    def __str__(self):
        return f"{self.driver} - {self.availability_status}"
    
class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        related_name='vehicles'
    )

    vehicle_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vehicle_number
    
class RideStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Requested'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    STARTED = 'STARTED', 'Started'
    DRIVER_ARRIVING = 'DRIVER_ARRIVING', 'Driver Arriving'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Ride(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides'
    )

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rides'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rides'
    )

    ride_type = models.ForeignKey(
    VehicleType,
    on_delete=models.PROTECT,
    related_name='rides',
    null=True,
    blank=True
)

    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=RideStatus.choices,
        default=RideStatus.REQUESTED
    )

    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['driver']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ride_type']),
        ]

    def __str__(self):
        return str(self.id)
    

ALLOWED_RIDE_TRANSITIONS = {
    RideStatus.REQUESTED: [
        RideStatus.ACCEPTED,
        RideStatus.CANCELLED,
    ],
    RideStatus.ACCEPTED: [
        RideStatus.DRIVER_ARRIVING,
        RideStatus.STARTED,
        RideStatus.CANCELLED,
    ],
    RideStatus.DRIVER_ARRIVING: [
        RideStatus.STARTED,
        RideStatus.CANCELLED,
    ],
    RideStatus.STARTED: [
        RideStatus.COMPLETED,
    ],
    RideStatus.COMPLETED: [],
    RideStatus.CANCELLED: [],
}    
    
