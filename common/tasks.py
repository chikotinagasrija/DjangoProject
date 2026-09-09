from celery import shared_task
from .models import Notification
from django.db.models import Count, Sum
from rides.models import Ride, RideStatus



@shared_task(queue="notifications")
def ride_notification(user_id, title, message, event_key):

    notification, created = Notification.objects.get_or_create(
        event_key=event_key,
        defaults={
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": "RIDE",
        }
    )

    if created:
        return "Ride notification created"

    return "Duplicate notification skipped"


@shared_task(queue="notifications")
def driver_assignment_notification(
    user_id,
    title,
    message,
    event_key
):

    notification, created = Notification.objects.get_or_create(
        event_key=event_key,
        defaults={
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": "RIDE",
        }
    )

    if created:
        return "Driver assignment notification created"

    return "Duplicate notification skipped"


@shared_task(queue="notifications")
def ride_completion_notification(
    user_id,
    title,
    message,
    event_key
):

    notification, created = Notification.objects.get_or_create(
        event_key=event_key,
        defaults={
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": "RIDE",
        }
    )

    if created:
        return "Ride completion notification created"

    return "Duplicate notification skipped"


@shared_task(queue="notifications")
def reminder_notification(
    user_id,
    title,
    message,
    event_key
):

    notification, created = Notification.objects.get_or_create(
        event_key=event_key,
        defaults={
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": "SYSTEM",
        }
    )

    if created:
        return "Reminder notification created"

    return "Duplicate notification skipped"



@shared_task(queue="reports")
def generate_ride_report():
    total_rides = Ride.objects.count()

    completed_rides = Ride.objects.filter(
        status=RideStatus.COMPLETED
    ).count()

    cancelled_rides = Ride.objects.filter(
        status=RideStatus.CANCELLED
    ).count()

    requested_rides = Ride.objects.filter(
        status=RideStatus.REQUESTED
    ).count()

    total_fare = Ride.objects.filter(
        status=RideStatus.COMPLETED
    ).aggregate(
        total=Sum("fare")
    )["total"] or 0

    return {
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "requested_rides": requested_rides,
        "total_fare": str(total_fare),
    }
@shared_task(queue="maintenance")
def clean_expired_data():
    """
    Cleanup task placeholder.

    Expiration rules are not currently defined
    in the project models.
    """

    return "No expiration rules configured"


@shared_task(queue="maintenance")
def process_background_records():
    """
    Background processing placeholder.

    A specific background-record processing
    workflow is not currently defined.
    """

    return "No background record processing configured"
from celery import shared_task


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def test_retry_task(self):
    print("Executing retry test task")
    raise Exception("Simulated temporary failure")