def create_notification(user, title, message, event_key):
    from common.models import Notification

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        event_key=event_key
    )