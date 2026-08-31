import math

from rides.models import DriverLocation


def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


def find_nearby_drivers(latitude, longitude, radius):

    drivers = []

    locations = DriverLocation.objects.filter(
        availability_status=DriverLocation.AvailabilityStatus.ONLINE,
        driver__is_active=True
    ).select_related(
        "driver",
        "driver__user"
    )

    for location in locations:

        distance = calculate_distance(
            latitude,
            longitude,
            float(location.latitude),
            float(location.longitude)
        )

        if distance <= radius:
            drivers.append({
                "driver_id": str(location.driver.id),
                "latitude": float(location.latitude),
                "longitude": float(location.longitude),
                "distance_km": round(distance, 2),
                "availability_status": location.availability_status
            })

    drivers.sort(
        key=lambda driver: driver["distance_km"]
    )

    return drivers