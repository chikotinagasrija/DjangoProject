from rides.models import DriverProfile, Ride, RideStatus
from rides.services.websocket_service import broadcast_driver_location


def get_driver_for_user(user):
    try:
        return DriverProfile.objects.get(user=user)
    except DriverProfile.DoesNotExist:
        return None


def is_driver_active(driver):
    return driver.is_active


def has_active_ride(driver):
    active_statuses = [
        RideStatus.ACCEPTED,
        RideStatus.DRIVER_ARRIVING,
        RideStatus.STARTED,
    ]

    return Ride.objects.filter(
        driver=driver,
        status__in=active_statuses
    ).exists()


def update_driver_location(driver, latitude, longitude):

    driver.latitude = latitude
    driver.longitude = longitude

    driver.save(
        update_fields=["latitude", "longitude"]
    )

    active_statuses = [
        RideStatus.ACCEPTED,
        RideStatus.DRIVER_ARRIVING,
        RideStatus.STARTED,
    ]

    ride = Ride.objects.filter(
        driver=driver,
        status__in=active_statuses
    ).first()

    if ride:
        broadcast_driver_location(
            ride.id,
            driver.latitude,
            driver.longitude
        )

    return driver

