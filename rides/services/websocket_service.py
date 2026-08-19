from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_ride_status(ride_id, status):
    channel_layer = get_channel_layer()

    print("CHANNEL LAYER:", channel_layer)
    print("BROADCAST GROUP:", f"ride_{ride_id}")
    print("BROADCAST STATUS:", status)


    async_to_sync(channel_layer.group_send)(
        f"ride_{ride_id}",
        {
            "type": "ride_status_update",
            "status": status,
        }
    )


def broadcast_driver_location(ride_id, latitude, longitude):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"ride_{ride_id}",
        {
            "type": "driver_location_update",
            "latitude": latitude,
            "longitude": longitude,
        }
    )
