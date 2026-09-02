from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken
from channels.layers import get_channel_layer


from config.asgi import application

from rides.models import (
    Ride,
    DriverProfile,
    VehicleType,
    RideStatus,
)


User = get_user_model()


class WebSocketTests(TransactionTestCase):

    def setUp(self):

        # Passenger
        self.user = User.objects.create_user(
            email="passenger@test.com",
            password="Test@12345",
            first_name="Passenger",
            last_name="User"
        )

        # Unauthorized user
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="Test@12345",
            first_name="Other",
            last_name="User"
        )

        # Driver
        self.driver_user = User.objects.create_user(
            email="driver@test.com",
            password="Test@12345",
            first_name="Driver",
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

        # Ride
        self.ride = Ride.objects.create(
            user=self.user,
            pickup_location="Hyderabad",
            drop_location="Secunderabad",
            ride_type=self.vehicle_type,
            status=RideStatus.REQUESTED
        )

    
    def get_access_token(self, user):
       refresh = RefreshToken.for_user(user)
       return str(refresh.access_token)

    def test_authenticated_passenger_can_connect(self):

        token =  self.get_access_token(self.user)

        async def run_test():

            communicator = WebsocketCommunicator(
                application,
                f"/ws/rides/{self.ride.id}/?token={token}"
            )

            connected, _ = await communicator.connect()

            self.assertTrue(connected)

            response = await communicator.receive_json_from()

            self.assertEqual(
                response["message"],
                f"Connected to ride {self.ride.id}"
            )

            await communicator.disconnect()

        async_to_sync(run_test)()

    def test_unauthenticated_user_rejected(self):

        async def run_test():

            communicator = WebsocketCommunicator(
                application,
                f"/ws/rides/{self.ride.id}/"
            )

            connected, close_code = await communicator.connect()

            self.assertFalse(connected)
            self.assertEqual(close_code, 4001)

        async_to_sync(run_test)()

    def test_invalid_token_rejected(self):

        async def run_test():

            communicator = WebsocketCommunicator(
                application,
                f"/ws/rides/{self.ride.id}/?token=invalid-token"
            )

            connected, close_code = await communicator.connect()

            self.assertFalse(connected)
            self.assertEqual(close_code, 4001)

        async_to_sync(run_test)()

    def test_unauthorized_user_rejected(self):

        token =  self.get_access_token(self.other_user)

        async def run_test():

            communicator = WebsocketCommunicator(
                application,
                f"/ws/rides/{self.ride.id}/?token={token}"
            )

            connected, close_code = await communicator.connect()

            self.assertFalse(connected)
            self.assertEqual(close_code, 4003)

        async_to_sync(run_test)()

    def test_assigned_driver_can_connect(self):

        # Keep database operation outside async function
        self.ride.driver = self.driver
        self.ride.save()

        token =  self.get_access_token(self.driver_user)

        async def run_test():

            communicator = WebsocketCommunicator(
                application,
                f"/ws/rides/{self.ride.id}/?token={token}"
            )

            connected, _ = await communicator.connect()

            self.assertTrue(connected)

            response = await communicator.receive_json_from()

            self.assertEqual(
                response["message"],
                f"Connected to ride {self.ride.id}"
            )

            await communicator.disconnect()

        async_to_sync(run_test)()

    def test_ride_status_event(self):

        token = self.get_access_token(self.user)
        async def run_test():

           communicator = WebsocketCommunicator(
               application,
               f"/ws/rides/{self.ride.id}/?token={token}"
        )

           connected, _ = await communicator.connect()

           self.assertTrue(connected)

        # Receive connection message
           await communicator.receive_json_from()

        # Get channel layer
           channel_layer = get_channel_layer()

        # Send ride status event
           await channel_layer.group_send(
               f"ride_{self.ride.id}",
            {
                   "type": "ride_status_update",
                   "status": "ACCEPTED",
            }
        )

           response = await communicator.receive_json_from()

           self.assertEqual(
             response["ride_id"],
             str(self.ride.id)
        )

           self.assertEqual(
            response["status"],
            "ACCEPTED"
        )

           await communicator.disconnect()

        async_to_sync(run_test)()
    def test_driver_location_event(self):
        token = self.get_access_token(self.user)
        async def run_test():

           communicator = WebsocketCommunicator(
               application,
               f"/ws/rides/{self.ride.id}/?token={token}"
        )

           connected, _ = await communicator.connect()

           self.assertTrue(connected)

        # Receive connection message
           await communicator.receive_json_from()

        # Get channel layer
           channel_layer = get_channel_layer()

        # Send driver location event
           await channel_layer.group_send(
               f"ride_{self.ride.id}",
            {
                "type": "driver_location_update",
                "latitude": 17.3850,
                "longitude": 78.4867,
            }
        )

           response = await communicator.receive_json_from()

           self.assertEqual(
            response["ride_id"],
            str(self.ride.id)
        )

           self.assertEqual(
            response["latitude"],
            17.3850
        )

           self.assertEqual(
            response["longitude"],
            78.4867
        )

           await communicator.disconnect()

        async_to_sync(run_test)()    
