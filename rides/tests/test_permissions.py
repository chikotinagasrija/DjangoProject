from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from rides.models import DriverProfile, Vehicle, VehicleType
from rides.permissions import (
    IsAdminOrOwnVehicle,
    IsAdminOrSelfDriver,
)


class PermissionTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            is_staff=True
        )

        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123",
            first_name="Driver",
            last_name="One"
        )

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            first_name="Other",
            last_name="User"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09AB1234",
            model="Honda City"
        )

        self.factory = APIRequestFactory()

    def test_admin_can_access_vehicle(self):
        request = self.factory.get("/")
        request.user = self.admin

        permission = IsAdminOrOwnVehicle()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.vehicle
            )
        )

    def test_owner_can_access_vehicle(self):
        request = self.factory.get("/")
        request.user = self.driver_user

        permission = IsAdminOrOwnVehicle()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.vehicle
            )
        )

    def test_other_user_cannot_access_vehicle(self):
        request = self.factory.get("/")
        request.user = self.other_user

        permission = IsAdminOrOwnVehicle()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.vehicle
            )
        )

    def test_admin_can_access_driver(self):
        request = self.factory.get("/")
        request.user = self.admin

        permission = IsAdminOrSelfDriver()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.driver
            )
        )

    def test_driver_can_access_own_profile(self):
        request = self.factory.get("/")
        request.user = self.driver_user

        permission = IsAdminOrSelfDriver()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.driver
            )
        )

    def test_other_user_cannot_access_driver(self):
        request = self.factory.get("/")
        request.user = self.other_user

        permission = IsAdminOrSelfDriver()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.driver
            )
        )