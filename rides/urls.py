from django.urls import path
from .views import (
    DriverListCreateAPIView,
    DriverDetailAPIView,
    RideCreateAPIView,
    VehicleListCreateAPIView,
    VehicleDetailAPIView,
    DriverNestedAPIView,
    RideDetailAPIView,
    RideStatusAPIView,
    RideAcceptAPIView,
    RideCancelAPIView,
    RideFareAPIView
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
    
    path("", RideCreateAPIView.as_view(), name="ride-create"),
    path("<uuid:pk>/", RideDetailAPIView.as_view(), name="ride-detail"),
    path("<uuid:pk>/status/", RideStatusAPIView.as_view(), name="ride-status"),
    path("<uuid:pk>/accept/", RideAcceptAPIView.as_view(), name="ride-accept"),
    path("<uuid:pk>/cancel/", RideCancelAPIView.as_view(), name="ride-cancel"),
    path("<uuid:pk>/fare/", RideFareAPIView.as_view(), name="ride-fare"),
]
