from django.test import TestCase
from django.contrib.auth import get_user_model

from rides.models import (
    DriverProfile,
    Ride,
    RideStatus,
    VehicleType,
)


class RideTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )

        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

    def test_create_ride(self):
        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        self.assertEqual(
            ride.status,
            RideStatus.REQUESTED
        )

        self.assertEqual(
            ride.user,
            self.user
        )

    def test_ride_can_be_assigned_to_driver(self):
        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        ride.driver = self.driver
        ride.status = RideStatus.ACCEPTED
        ride.save()

        self.assertEqual(
            ride.driver,
            self.driver
        )

        self.assertEqual(
            ride.status,
            RideStatus.ACCEPTED
        )