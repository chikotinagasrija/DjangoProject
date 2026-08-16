from rides.models import DriverProfile, Ride, RideStatus


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
