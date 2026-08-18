from django.urls import path
from .views import (
    DriverListCreateAPIView,
    DriverDetailAPIView,
    LargeDatasetPerformanceAPIView,
    RideIndexPerformanceAPIView,
    VehicleListCreateAPIView,
    VehicleDetailAPIView,
    DriverNestedAPIView,
    RideDetailAPIView,
    RideStatusAPIView,
    RideAcceptAPIView,
    RideCancelAPIView,
    RideFareAPIView,
    UserActiveRidesAPIView,
    UserCompletedRidesAPIView,
    UserCancelledRidesAPIView,
    DriverRideHistoryAPIView,
    DailyRideCountAPIView,
    TotalCompletedRidesAPIView,
    DriverTotalFareAPIView,
    RideAggregationAPIView,
    SlowRideListAPIView,
    OptimizedRideListAPIView,
    DriverVehicleListAPIView,
    AdvancedRideFilterAPIView,
    RideListCreateAPIView,
    DriverLocationAPIView,
    NearbyDriverAPIView,
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
    path(
    "my/active/",
    UserActiveRidesAPIView.as_view(),
    name="user-active-rides"
),

    path(
    "my/completed/",
    UserCompletedRidesAPIView.as_view(),
    name="user-completed-rides"
),

    path(
    "my/cancelled/",
    UserCancelledRidesAPIView.as_view(),
    name="user-cancelled-rides"
),

    path(
    "driver/history/",
    DriverRideHistoryAPIView.as_view(),
    name="driver-ride-history"
),

    path(
    "driver/daily-count/",
    DailyRideCountAPIView.as_view(),
    name="driver-daily-count"
),

    path(
    "driver/completed-count/",
    TotalCompletedRidesAPIView.as_view(),
    name="driver-completed-count"
),

    path(
    "driver/total-fare/",
    DriverTotalFareAPIView.as_view(),
    name="driver-total-fare"
),

    path(
    "aggregations/",
    RideAggregationAPIView.as_view(),
    name="ride-aggregations"
),
    path(
    "slow/",
    SlowRideListAPIView.as_view(),
    name="slow-ride-list"
),

    path(
    "optimized/",
    OptimizedRideListAPIView.as_view(),
    name="optimized-ride-list"
),

    path(
    "driver-vehicles/",
    DriverVehicleListAPIView.as_view(),
    name="driver-vehicle-list"
),
    path(
    "index-performance/",
    RideIndexPerformanceAPIView.as_view(),
    name="index-performance"
),
    path(
    "filter/",
    AdvancedRideFilterAPIView.as_view(),
    name="advanced-ride-filter"
),
    path(
    "",
    RideListCreateAPIView.as_view(),
    name="ride-list-create"
),
    path(
    "performance/",
    LargeDatasetPerformanceAPIView.as_view(),
    name="large-dataset-performance"
),
    path(
    'drivers/nearby/',
    NearbyDriverAPIView.as_view(),
    name='nearby-drivers'
),

    
    path("<uuid:pk>/", RideDetailAPIView.as_view(), name="ride-detail"),
    path("<uuid:pk>/status/", RideStatusAPIView.as_view(), name="ride-status"),
    path("<uuid:pk>/accept/", RideAcceptAPIView.as_view(), name="ride-accept"),
    path("<uuid:pk>/cancel/", RideCancelAPIView.as_view(), name="ride-cancel"),
    path("<uuid:pk>/fare/", RideFareAPIView.as_view(), name="ride-fare"),
    path("<uuid:pk>/", RideDetailAPIView.as_view(), name="ride-detail"),
    path("drivers/location/", DriverLocationAPIView.as_view(), name="driver-location"),
]
