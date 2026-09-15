from django.urls import path

from .views import (
    DatabaseHealthCheckAPIView,
    NotificationListAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
    HealthCheckAPIView,
    DatabaseHealthCheckAPIView,
    RedisHealthCheckAPIView,
)


urlpatterns = [
    path(
        "health/",
        HealthCheckAPIView.as_view(),
        name="health-check",
    ),

    path(
        "health/database/",
        DatabaseHealthCheckAPIView.as_view(),
        name="database-health-check",
    ),

    path(
        "health/redis/",
        RedisHealthCheckAPIView.as_view(),
        name="redis-health-check",
    ),


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