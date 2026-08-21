from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter

from rides.models import Ride, DriverProfile, RideStatus, VehicleType
from rides.consumers import RideConsumer

from django.urls import re_path


application = URLRouter([
    re_path(
        r"ws/rides/(?P<ride_id>[^/]+)/$",
        RideConsumer.as_asgi()
    ),
])


class WebSocketTests(TransactionTestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )

        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123",
            first_name="Driver",
            last_name="Test"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="DL12345",
            is_active=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Sedan"
        )

        self.ride = Ride.objects.create(
            user=self.user,
            driver=self.driver,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

    async def test_passenger_connection(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/"
        )

        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()

        self.assertEqual(
            response["message"],
            f"Connected to ride {self.ride.id}"
        )

        await communicator.disconnect()

    async def test_driver_connection(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/"
        )

        communicator.scope["user"] = self.driver_user

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.receive_json_from()

        await communicator.disconnect()

    async def test_unauthorized_user_rejected(self):
        User = get_user_model()

        other_user = await database_sync_to_async(
    User.objects.create_user
)(
    email="other@test.com",
    password="testpass123",
    first_name="Other",
    last_name="User"
)

        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/"
        )

        communicator.scope["user"] = other_user

        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4003)

    async def test_driver_location_message(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/"
        )

        communicator.scope["user"] = self.user

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.receive_json_from()

        await communicator.send_json_to({
            "test": "message"
        })

        await communicator.disconnect()