from django.urls import path

from .views import (
    NotificationListAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
)

urlpatterns = [

    path(
        "notifications/",
        NotificationListAPIView.as_view(),
        name="notifications"
    ),

    path(
        "notifications/<int:pk>/read/",
        NotificationMarkReadAPIView.as_view(),
        name="notification-read"
    ),

    path(
        "notifications/read-all/",
        NotificationMarkAllReadAPIView.as_view(),
        name="notifications-read-all"
    ),
]