from django.urls import path
from .views import (
    DriverListCreateAPIView,
    DriverDetailAPIView,
    VehicleListCreateAPIView,
    VehicleDetailAPIView,
    DriverNestedAPIView
)

urlpatterns = [
    path(
        'drivers/',
        DriverListCreateAPIView.as_view(),
        name='driver-list-create'
    ),

    path(
        'drivers/<uuid:pk>/',
        DriverDetailAPIView.as_view(),
        name='driver-detail'
    ),

    path(
        'vehicles/',
        VehicleListCreateAPIView.as_view(),
        name='vehicle-list-create'
    ),

    path(
        'vehicles/<uuid:pk>/',
        VehicleDetailAPIView.as_view(),
        name='vehicle-detail'
    ),
    path(
    'drivers/<uuid:pk>/details/',
    DriverNestedAPIView.as_view(),
),
]