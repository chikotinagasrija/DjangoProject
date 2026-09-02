from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model


from rides.models import (
    DriverProfile,
    DriverLocation,
    Ride,
    RideStatus,
    VehicleType,
)

from rides.services.fare_service import calculate_fare
from rides.services.driver_service import (
    get_driver_for_user,
    is_driver_active,
    has_active_ride,
)

from rides.services.nearby_driver_service import find_nearby_drivers
from rides.services.ride_service import (
    accept_ride,
    cancel_ride,
    update_ride_status,
)


User = get_user_model()


class BusinessLogicTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="passenger@test.com",
            password="Test@12345",
            first_name="Passenger",
            last_name="User"
        )

        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="Test@12345",
            first_name="Driver",
            last_name="User"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True,
            latitude=17.3850,
            longitude=78.4867
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

    # -------------------------------------------------
    # 1. FARE CALCULATION
    # -------------------------------------------------

    def test_fare_calculation(self):
        fare = calculate_fare(
            distance_km=10,
            duration_minutes=20
        )

        # 40 + (10 * 8) + (20 * 1) + 10 = 150
        self.assertEqual(
            fare["total"],
            Decimal("150.00")
        )

        self.assertEqual(
            fare["base_fare"],
            Decimal("40.00")
        )

        self.assertEqual(
            fare["distance_fare"],
            Decimal("80.00")
        )

        self.assertEqual(
            fare["time_fare"],
            Decimal("20.00")
        )

        self.assertEqual(
            fare["surge"],
            Decimal("10.00")
        )

    def test_negative_distance_rejected(self):
        with self.assertRaises(ValueError):
            calculate_fare(
                distance_km=-5,
                duration_minutes=20
            )

    def test_negative_duration_rejected(self):
        with self.assertRaises(ValueError):
            calculate_fare(
                distance_km=10,
                duration_minutes=-20
            )

    # -------------------------------------------------
    # 2. DRIVER AVAILABILITY
    # -------------------------------------------------

    def test_get_driver_for_user(self):
        driver = get_driver_for_user(
            self.driver_user
        )

        self.assertEqual(
            driver,
            self.driver
        )

    def test_get_driver_for_non_driver(self):
        driver = get_driver_for_user(
            self.user
        )

        self.assertIsNone(driver)

    def test_active_driver(self):
        self.assertTrue(
            is_driver_active(self.driver)
        )

    def test_inactive_driver(self):
        self.driver.is_active = False
        self.driver.save()

        self.assertFalse(
            is_driver_active(self.driver)
        )

        # -------------------------------------------------
    # 3. NEARBY DRIVER SELECTION
    # -------------------------------------------------

    def test_nearby_online_driver_is_selected(self):

        DriverLocation.objects.create(
            driver=self.driver,
            latitude=17.3850,
            longitude=78.4867,
            availability_status=DriverLocation.AvailabilityStatus.ONLINE
        )

        nearby_drivers = find_nearby_drivers(
            latitude=17.3850,
            longitude=78.4867,
            radius=5
        )

        self.assertEqual(len(nearby_drivers), 1)

        self.assertEqual(
            nearby_drivers[0]["driver_id"],
            str(self.driver.id)
        )

    def test_driver_outside_radius_is_not_selected(self):

        DriverLocation.objects.create(
            driver=self.driver,
            latitude=17.5000,
            longitude=78.7000,
            availability_status=DriverLocation.AvailabilityStatus.ONLINE
        )

        nearby_drivers = find_nearby_drivers(
            latitude=17.3850,
            longitude=78.4867,
            radius=1
        )

        self.assertEqual(
            len(nearby_drivers),
            0
        )

    def test_offline_driver_is_not_selected(self):

        DriverLocation.objects.create(
            driver=self.driver,
            latitude=17.3850,
            longitude=78.4867,
            availability_status=DriverLocation.AvailabilityStatus.OFFLINE
        )

        nearby_drivers = find_nearby_drivers(
            latitude=17.3850,
            longitude=78.4867,
            radius=5
        )

        self.assertEqual(
            len(nearby_drivers),
            0
        )

    def test_inactive_driver_is_not_selected(self):

        self.driver.is_active = False
        self.driver.save()

        DriverLocation.objects.create(
            driver=self.driver,
            latitude=17.3850,
            longitude=78.4867,
            availability_status=DriverLocation.AvailabilityStatus.ONLINE
        )

        nearby_drivers = find_nearby_drivers(
            latitude=17.3850,
            longitude=78.4867,
            radius=5
        )

        self.assertEqual(
            len(nearby_drivers),
            0
        )    

    # -------------------------------------------------
    # 3. ACTIVE RIDE CHECK
    # -------------------------------------------------

    def test_driver_without_active_ride(self):
        self.assertFalse(
            has_active_ride(self.driver)
        )

    def test_driver_with_active_ride(self):
        Ride.objects.create(
            user=self.user,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.ACCEPTED
        )

        self.assertTrue(
            has_active_ride(self.driver)
        )

    # -------------------------------------------------
    # 4. RIDE ACCEPTANCE
    # -------------------------------------------------

    def test_active_driver_can_accept_ride(self):

        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        accepted_ride = accept_ride(
            ride,
            self.driver
        )

        self.assertEqual(
            accepted_ride.driver,
            self.driver
        )

        self.assertEqual(
            accepted_ride.status,
            RideStatus.ACCEPTED
        )

    def test_inactive_driver_cannot_accept_ride(self):

        self.driver.is_active = False
        self.driver.save()

        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        with self.assertRaises(ValueError):
            accept_ride(
                ride,
                self.driver
            )

    # -------------------------------------------------
    # 5. CANCELLATION RULES
    # -------------------------------------------------

    def test_requested_ride_can_be_cancelled(self):

        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        cancel_ride(ride)

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            RideStatus.CANCELLED
        )

    def test_started_ride_cannot_be_cancelled(self):

        ride = Ride.objects.create(
            user=self.user,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.STARTED
        )

        with self.assertRaises(ValueError):
            cancel_ride(ride)

    def test_completed_ride_cannot_be_cancelled(self):

        ride = Ride.objects.create(
            user=self.user,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.COMPLETED
        )

        with self.assertRaises(ValueError):
            cancel_ride(ride)

    # -------------------------------------------------
    # 6. INVALID STATUS TRANSITION
    # -------------------------------------------------

    def test_invalid_ride_status_transition(self):

        ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

        with self.assertRaises(ValueError):
            update_ride_status(
                ride,
                RideStatus.COMPLETED
            )