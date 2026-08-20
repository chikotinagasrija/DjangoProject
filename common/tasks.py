from celery import shared_task
from .models import Notification


@shared_task
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


@shared_task
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


@shared_task
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


@shared_task
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