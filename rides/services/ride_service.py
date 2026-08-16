from django.db import transaction

from rides.models import (
    Ride,
    RideStatus,
    ALLOWED_RIDE_TRANSITIONS,
)


def update_ride_status(ride, new_status):
    current_status = ride.status

    allowed_statuses = ALLOWED_RIDE_TRANSITIONS.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid status transition: "
            f"{current_status} → {new_status}"
        )

    ride.status = new_status
    ride.save()

    return ride

@transaction.atomic
def accept_ride(ride, driver):
    # Lock this ride row until the transaction finishes
    ride = Ride.objects.select_for_update().get(id=ride.id)

    if not driver.is_active:
        raise ValueError("Driver is not active.")

    if ride.status != RideStatus.REQUESTED:
        raise ValueError("Ride is no longer available.")


    

    active_statuses = [
        RideStatus.ACCEPTED,
        RideStatus.DRIVER_ARRIVING,
        RideStatus.STARTED,
    ]

    if Ride.objects.filter(
        driver=driver,
        status__in=active_statuses
    ).exists():
        raise ValueError(
            "Driver already has an active ride."
        )

    ride.driver = driver
    ride.status = RideStatus.ACCEPTED
    ride.save()

    return ride


def cancel_ride(ride):
    allowed_statuses = [
        RideStatus.REQUESTED,
        RideStatus.ACCEPTED,
        RideStatus.DRIVER_ARRIVING,
    ]

    if ride.status not in allowed_statuses:
        raise ValueError(
            "Ride cannot be cancelled in its current status."
        )

    ride.status = RideStatus.CANCELLED
    ride.save()

    return ride
@transaction.atomic
def complete_ride(ride, fare):
    ride.fare = fare
    ride.status = RideStatus.COMPLETED
    ride.save()

    return ride
