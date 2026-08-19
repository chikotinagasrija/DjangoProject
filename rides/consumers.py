from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Ride
import json


class RideConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_ride_and_authorize_user(self, user, ride_id):

        try:
            ride = Ride.objects.select_related(
                "user",
                "driver__user"
            ).get(id=ride_id)

        except Ride.DoesNotExist:
            return False

        # Passenger authorization
        if ride.user_id == user.id:
            return True

        # Driver authorization
        if ride.driver and ride.driver.user_id == user.id:
            return True

        return False

    async def connect(self):

        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]

        user = self.scope.get("user")

        # 1. JWT authentication check
        if not user or not user.is_authenticated:
            print("WebSocket rejected: Invalid or missing JWT")
            await self.close(code=4001)
            return

        # 2. Ride ownership / driver authorization
        authorized = await self.get_ride_and_authorize_user(
            user,
            self.ride_id
        )

        if not authorized:
            print(
                f"WebSocket rejected: User {user.id} "
                f"is not authorized for ride {self.ride_id}"
            )
            await self.close(code=4003)
            return

        # 3. Create ride group
        self.ride_group_name = f"ride_{self.ride_id}"

        await self.channel_layer.group_add(
            self.ride_group_name,
            self.channel_name
        )

        # 4. Accept connection
        await self.accept()

        print(
            f"WebSocket connected: "
            f"user={user.id}, ride={self.ride_id}"
        )

        await self.send(text_data=json.dumps({
            "message": f"Connected to ride {self.ride_id}"
        }))

    async def disconnect(self, close_code):

        # Remove connection from ride group
        if hasattr(self, "ride_group_name"):
            await self.channel_layer.group_discard(
                self.ride_group_name,
                self.channel_name
            )

        print(
            f"WebSocket disconnected: "
            f"ride={getattr(self, 'ride_id', None)}, "
            f"close_code={close_code}"
        )

    async def receive(self, text_data):
        pass

    async def ride_status_update(self, event):

        print("EVENT RECEIVED BY WEBSOCKET:", event)

        await self.send(text_data=json.dumps({
            "ride_id": str(self.ride_id),
            "status": event["status"],
        }))

    async def driver_location_update(self, event):

        await self.send(text_data=json.dumps({
            "ride_id": str(self.ride_id),
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        }))