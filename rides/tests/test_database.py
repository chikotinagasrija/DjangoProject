from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from rides.models import (
    DriverProfile,
    Vehicle,
    VehicleType,
    Ride,
    RideStatus,
)


User = get_user_model()


class DatabaseTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            email="user@test.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="Test@12345",
            first_name="Test",
            last_name="Driver"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

    # -------------------------------------------------
    # 1. UNIQUE FIELD TESTS
    # -------------------------------------------------

    def test_user_email_must_be_unique(self):

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="user@test.com",
                password="Test@12345",
                first_name="Another",
                last_name="User"
            )

    def test_license_number_must_be_unique(self):

        with self.assertRaises(IntegrityError):
            DriverProfile.objects.create(
                user=User.objects.create_user(
                    email="driver2@test.com",
                    password="Test@12345",
                    first_name="Driver",
                    last_name="Two"
                ),
                license_number="DL12345"
            )

    def test_vehicle_type_name_must_be_unique(self):

        with self.assertRaises(IntegrityError):
            VehicleType.objects.create(
                name="Sedan"
            )

    # -------------------------------------------------
    # 2. FOREIGN KEY / RELATIONSHIP TESTS
    # -------------------------------------------------

    def test_vehicle_belongs_to_driver(self):

        vehicle = Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09AB1234",
            model="Honda City"
        )

        self.assertEqual(
            vehicle.driver,
            self.driver
        )

    def test_ride_belongs_to_user(self):

        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        self.assertEqual(
            ride.user,
            self.user
        )

    # -------------------------------------------------
    # 3. REQUIRED FIELD TESTS
    # -------------------------------------------------

    def test_driver_license_number_required(self):

        with self.assertRaises(IntegrityError):
            DriverProfile.objects.create(
                user=self.driver_user,
                license_number=None
            )

    def test_vehicle_number_required(self):

        with self.assertRaises(IntegrityError):
            Vehicle.objects.create(
                driver=self.driver,
                vehicle_type=self.vehicle_type,
                vehicle_number=None,
                model="Honda City"
            )

    # -------------------------------------------------
    # 4. MODEL CONSTRAINT TESTS
    # -------------------------------------------------

    def test_driver_user_one_to_one_constraint(self):

        another_driver = User.objects.create_user(
            email="driver3@test.com",
            password="Test@12345",
            first_name="Driver",
            last_name="Three"
        )

        with self.assertRaises(IntegrityError):
            DriverProfile.objects.create(
                user=self.driver_user,
                license_number="DL99999"
            )

    def test_vehicle_number_unique(self):

        Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09AB1234",
            model="Honda City"
        )

        another_driver_user = User.objects.create_user(
            email="driver4@test.com",
            password="Test@12345",
            first_name="Driver",
            last_name="Four"
        )

        another_driver = DriverProfile.objects.create(
            user=another_driver_user,
            license_number="DL88888"
        )

        with self.assertRaises(IntegrityError):
            Vehicle.objects.create(
                driver=another_driver,
                vehicle_type=self.vehicle_type,
                vehicle_number="TS09AB1234",
                model="Toyota"
            )

    

    