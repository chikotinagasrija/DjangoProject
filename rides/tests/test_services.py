from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rides.models import (
    DriverProfile,
    Ride,
    RideStatus,
    VehicleType,
)

from rides.services.fare_service import calculate_fare
from rides.services.ride_service import (
    accept_ride,
    cancel_ride,
    update_ride_status,
)


class RideServiceTests(TestCase):

    def setUp(self):
        User = get_user_model()

        # Create rider
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )

        # Create driver user
        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123"
        )

        # Create driver profile
        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True
        )

        # Create vehicle type
        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

        # Create requested ride
        self.ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

    # 1. Fare Calculation Test
    def test_fare_calculation(self):
        result = calculate_fare(
            distance_km=10,
            duration_minutes=20
        )

        self.assertEqual(
            result["base_fare"],
            Decimal("40.00")
        )

        self.assertEqual(
            result["distance_fare"],
            Decimal("80.00")
        )

        self.assertEqual(
            result["time_fare"],
            Decimal("20.00")
        )

        self.assertEqual(
            result["surge"],
            Decimal("10.00")
        )

        self.assertEqual(
            result["total"],
            Decimal("150.00")
        )

    # 2. Ride Acceptance Test
    def test_ride_acceptance(self):
        ride = accept_ride(
            self.ride,
            self.driver
        )

        self.assertEqual(
            ride.status,
            RideStatus.ACCEPTED
        )

        self.assertEqual(
            ride.driver,
            self.driver
        )

    # 3. Ride Cancellation Test
    def test_ride_cancellation(self):
        ride = cancel_ride(self.ride)

        self.assertEqual(
            ride.status,
            RideStatus.CANCELLED
        )

    # 4. Invalid State Change Test
    def test_invalid_state_change(self):
        self.ride.status = RideStatus.STARTED
        self.ride.save()

        with self.assertRaises(ValueError):
            cancel_ride(self.ride)

    # 5. Duplicate Ride Acceptance Test
    def test_duplicate_ride_acceptance(self):
        # First driver accepts the ride
        accept_ride(
            self.ride,
            self.driver
        )

        # Create second driver
        second_driver_user = get_user_model().objects.create_user(
            email="driver2@test.com",
            password="testpass123"
        )

        second_driver = DriverProfile.objects.create(
            user=second_driver_user,
            license_number="DL67890",
            is_active=True
        )

        # Second driver should be rejected
        with self.assertRaises(ValueError):
            accept_ride(
                self.ride,
                second_driver
            )
