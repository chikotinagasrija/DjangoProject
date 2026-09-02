from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from rides.models import (
    DriverProfile,
    Ride,
    RideStatus,
    VehicleType,
)


# -----------------------------------------
# Existing Model Tests
# -----------------------------------------

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


# -----------------------------------------
# Task 4 - Ride API Tests
# -----------------------------------------

class RideAPITests(APITestCase):

    def setUp(self):

        User = get_user_model()

        # Passenger
        self.passenger = User.objects.create_user(
            email="passenger@test.com",
            password="testpass123"
        )

        # Driver
        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123"
        )

        # Driver Profile
        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL99999",
            is_active=True
        )

        # Vehicle Type
        self.vehicle_type = VehicleType.objects.create(
            name="Car"
        )

        # Authenticate as passenger
        self.client.force_authenticate(
            user=self.passenger
        )

    # -----------------------------------------
    # 1. Create Ride
    # -----------------------------------------

    def test_create_ride_api(self):

        data = {
            "pickup_location": "Hyderabad",
            "drop_location": "Secunderabad",
            "ride_type": str(self.vehicle_type.id),
        }

        response = self.client.post(
            "/api/v1/rides/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        ride = Ride.objects.get(
            user=self.passenger
        )

        self.assertEqual(
            ride.status,
            RideStatus.REQUESTED
        )

    # -----------------------------------------
    # 2. Accept Ride
    # -----------------------------------------

    def test_accept_ride_api(self):

        ride = Ride.objects.create(
            user=self.passenger,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.post(
            f"/api/v1/rides/{ride.id}/accept/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.ACCEPTED
        )

        self.assertEqual(
            ride.driver,
            self.driver
        )

    # -----------------------------------------
    # 3. Start Ride
    # -----------------------------------------

    def test_start_ride_api(self):

        ride = Ride.objects.create(
            user=self.passenger,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.ACCEPTED
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.patch(
            f"/api/v1/rides/{ride.id}/status/",
            {
                "status": RideStatus.STARTED
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.STARTED
        )

    # -----------------------------------------
    # 4. Complete Ride
    # -----------------------------------------

    def test_complete_ride_api(self):

        ride = Ride.objects.create(
            user=self.passenger,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.STARTED
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.patch(
            f"/api/v1/rides/{ride.id}/status/",
            {
                "status": RideStatus.COMPLETED
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.COMPLETED
        )

    # -----------------------------------------
    # 5. Cancel Ride
    # -----------------------------------------

    def test_cancel_ride_api(self):

        ride = Ride.objects.create(
            user=self.passenger,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        self.client.force_authenticate(
            user=self.passenger
        )

        response = self.client.post(
            f"/api/v1/rides/{ride.id}/cancel/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.CANCELLED
        )

    # -----------------------------------------
    # 6. Invalid Status Transition
    # -----------------------------------------

    def test_invalid_status_transition_api(self):

        ride = Ride.objects.create(
            user=self.passenger,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.COMPLETED
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.patch(
            f"/api/v1/rides/{ride.id}/status/",
            {
                "status": RideStatus.STARTED
            },
            format="json"
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.COMPLETED
        )