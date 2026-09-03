from django.db import transaction

from rides.models import (
    Ride,
    RideStatus,
    ALLOWED_RIDE_TRANSITIONS,
)
from rides.services.websocket_service import broadcast_ride_status

from common.tasks import (
    driver_assignment_notification,
    ride_completion_notification,
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
    ride.save(update_fields=["status"])

    # Broadcast the new status to connected clients
    broadcast_ride_status(
        ride.id,
        new_status
    )

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

    ride.save(
        update_fields=["driver", "status"]
    )

    # Broadcast ACCEPTED status
    broadcast_ride_status(
        ride.id,
        RideStatus.ACCEPTED
    )

    # Send notification only after transaction commits
    transaction.on_commit(
        lambda: driver_assignment_notification.delay(
            ride.user.id,
            "Driver Assigned",
            "A driver has been assigned to your ride.",
            f"{ride.id}:DRIVER_ASSIGNED"
        )
    )

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

    ride.save(
        update_fields=["status"]
    )

    # Broadcast CANCELLED status
    broadcast_ride_status(
        ride.id,
        RideStatus.CANCELLED
    )

    return ride


@transaction.atomic
def complete_ride(ride, fare):
    ride.fare = fare
    ride.status = RideStatus.COMPLETED

    ride.save(
        update_fields=["fare", "status"]
    )

    # Broadcast COMPLETED status
    broadcast_ride_status(
        ride.id,
        RideStatus.COMPLETED
    )

    # Send notification only after transaction commits
    transaction.on_commit(
        lambda: ride_completion_notification.delay(
            ride.user.id,
            "Ride Completed",
            "Your ride has been completed.",
            f"{ride.id}:RIDE_COMPLETED"
        )
    )

    return ride
def save_ride_fare(ride, fare):
    ride.fare = fare["total"]
    ride.save(update_fields=["fare"])
    return ride
def get_ride_history(user, query_params):
    rides = Ride.objects.filter(
        user=user
    ).select_related(
        "user",
        "driver",
        "vehicle",
        "ride_type"
    )

    start_date = query_params.get("start_date")
    end_date = query_params.get("end_date")

    if start_date:
        rides = rides.filter(
            created_at__date__gte=start_date
        )

    if end_date:
        rides = rides.filter(
            created_at__date__lte=end_date
        )

    status_value = query_params.get("status")

    if status_value:
        rides = rides.filter(
            status=status_value
        )

    driver_id = query_params.get("driver_id")

    if driver_id:
        rides = rides.filter(
            driver_id=driver_id
        )

    min_fare = query_params.get("min_fare")
    max_fare = query_params.get("max_fare")

    if min_fare:
        rides = rides.filter(
            fare__gte=min_fare
        )

    if max_fare:
        rides = rides.filter(
            fare__lte=max_fare
        )

    

    return rides