from django.test import TestCase
from django.contrib.auth import get_user_model

from rides.models import (
    DriverProfile,
    Vehicle,
    VehicleType,
)


class VehicleTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123"
        )

        self.driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL12345",
            is_active=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

    def test_create_vehicle(self):
        vehicle = Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09AB1234",
            model="Honda City"
        )

        self.assertEqual(
            vehicle.vehicle_number,
            "TS09AB1234"
        )

        self.assertEqual(
            vehicle.driver,
            self.driver
        )

    def test_vehicle_type(self):
        vehicle = Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09CD5678",
            model="Hyundai"
        )

        self.assertEqual(
            vehicle.vehicle_type,
            self.vehicle_type
        )