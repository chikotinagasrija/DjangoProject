from django.urls import path

from .views import (
    HealthCheckAPIView,
    DatabaseHealthCheckAPIView,
    RedisHealthCheckAPIView,
)


urlpatterns = [
    path("", HealthCheckAPIView.as_view(), name="health-check"),
    path(
        "database/",
        DatabaseHealthCheckAPIView.as_view(),
        name="database-health-check",
    ),
    path(
        "redis/",
        RedisHealthCheckAPIView.as_view(),
        name="redis-health-check",
    ),
]