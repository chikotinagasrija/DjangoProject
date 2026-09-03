from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import DriverProfile, Vehicle,Ride,RideStatus, DriverLocation,VehicleType
from rest_framework.permissions import IsAuthenticated
from .serializers import DriverProfileSerializer, VehicleSerializer,DriverNestedSerializer,RideSerializer,RideStatusSerializer,DriverLocationSerializer
from .permissions import IsAdminOrOwnVehicle, IsAdminOrSelfDriver
from django.shortcuts import get_object_or_404
from .services.fare_service import calculate_fare
from django.db.models import Count,Sum,Avg,Min,Max,Q,F
from django.utils import timezone
from django.db import connection, reset_queries
from django.core.cache import cache
from rides.services.nearby_driver_service import find_nearby_drivers
from rides.services.driver_service import update_driver_location
from rides.services.ride_service import save_ride_fare
from rides.services.ride_service import get_ride_history
from django.db import connection, reset_queries
from rides.utils.helpers import success_response, error_response
from rides.utils.throttles import RideCreationThrottle
from .services.websocket_service import broadcast_driver_location
from rest_framework.pagination import PageNumberPagination
import time
import math


from .services.ride_service import (
    update_ride_status,
    accept_ride,
    cancel_ride,
)
from .services.websocket_service import (
    broadcast_ride_status,
    broadcast_driver_location,
)
def apply_ride_filters(queryset, params):
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    status = params.get("status")
    driver_id = params.get("driver_id")
    min_fare = params.get("min_fare")
    max_fare = params.get("max_fare")

    if start_date:
        queryset = queryset.filter(
            created_at__date__gte=start_date
        )

    if end_date:
        queryset = queryset.filter(
            created_at__date__lte=end_date
        )

    if status:
        queryset = queryset.filter(
            status=status
        )

    if driver_id:
        queryset = queryset.filter(
            driver_id=driver_id
        )

    if min_fare:
        queryset = queryset.filter(
            fare__gte=min_fare
        )

    if max_fare:
        queryset = queryset.filter(
            fare__lte=max_fare
        )

    return queryset

class DriverListCreateAPIView(generics.ListCreateAPIView):
    queryset = DriverProfile.objects.select_related('user')
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAdminOrSelfDriver]
    

    filterset_fields = ['rating']
    search_fields = [
        'license_number',
        'user__email',
        'rating',
        'is_active'
    ]
    ordering_fields = [
        'rating',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']

class VehicleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.select_related('driver', 'vehicle_type', 'driver__user')
    
    

    filterset_fields = [
        'vehicle_type',
    ]

    search_fields = [
        'vehicle_number',
        'model',
        'driver__license_number',
        'driver__user__email',
    ]

    ordering_fields = [
        'vehicle_number',
        'model',
        'created_at',
        'updated_at',
    ]

    ordering = ['-created_at']

class DriverDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer

class VehicleDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrOwnVehicle]
    
class DriverNestedAPIView(generics.RetrieveAPIView):
    queryset = DriverProfile.objects.prefetch_related('vehicles__vehicle_type')
    serializer_class = DriverNestedSerializer

class RideDetailAPIView(generics.RetrieveAPIView):
    queryset = Ride.objects.select_related(
        'user',
        'driver',
        'vehicle',
        'ride_type'
    )
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return self.queryset.filter(
            Q(user=user) |
            Q(driver__user=user)
        ).distinct()

class RideStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        ride = get_object_or_404(Ride, id=pk)

        serializer = RideStatusSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        try:
            ride = update_ride_status(
                ride,
                new_status
            )
        except ValueError as exc:
             return Response(
        {
            "success": False,
            "message": str(exc),
            "error_code": "INVALID_RIDE_STATUS",
            "data": None
        },
        status=status.HTTP_400_BAD_REQUEST
    )

        return Response(
            {
                "message": "Ride status updated successfully.",
                "ride_id": str(ride.id),
                "status": ride.status,
            },
            status=status.HTTP_200_OK
        )
          
class RideAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ride = get_object_or_404(Ride, id=pk)

        driver = get_object_or_404(
            DriverProfile,
            user=request.user
        )

        try:
            ride = accept_ride(ride, driver)
        except ValueError as exc:
            return Response(
        {
            "success": False,
            "message": str(exc),
            "error_code": "RIDE_ACCEPT_FAILED",
            "data": None
        },
        status=status.HTTP_400_BAD_REQUEST
    )

        return Response(
            {
                "message": "Ride accepted successfully.",
                "ride_id": str(ride.id),
                "driver": str(ride.driver.id),
                "status": ride.status,
            },
            status=status.HTTP_200_OK
        )

class RideCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ride = get_object_or_404(Ride, id=pk)

        try:
            ride = cancel_ride(ride)
        except ValueError as exc:
            return Response(
        {
            "success": False,
            "message": str(exc),
            "error_code": "INVALID_RIDE_STATUS",
            "data": None
        },
        status=status.HTTP_400_BAD_REQUEST
    )
        return Response(
            {
                "message": "Ride cancelled successfully.",
                "ride_id": str(ride.id),
                "status": ride.status,
            },
            status=status.HTTP_200_OK
        ) 
class RideFareAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        ride = get_object_or_404(Ride, id=pk)

        distance_km = request.data.get("distance_km")
        duration_minutes = request.data.get("duration_minutes")

        if distance_km is None or duration_minutes is None:
            return Response(
                {
                    "error": "distance_km and duration_minutes are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fare = calculate_fare(
                distance_km=distance_km,
                duration_minutes=duration_minutes,
            )
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "Invalid distance or duration."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save calculated fare to the Ride
        save_ride_fare(ride, fare)

        return Response(
            {
                "base fare": fare["base_fare"],
                "distance_fare": fare["distance_fare"],
                "time_fare": fare["time_fare"],
                "surge": fare["surge"],
                "total": fare["total"],
            },
            status=status.HTTP_200_OK
        )     

class UserActiveRidesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        active_statuses = [
            RideStatus.REQUESTED,
            RideStatus.ACCEPTED,
            RideStatus.DRIVER_ARRIVING,
            RideStatus.STARTED,
        ]

        rides = Ride.objects.filter(
            user=request.user,
            status__in=active_statuses
        ).select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        )

        # Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            rides = rides.filter(
                created_at__date__gte=start_date
            )

        if end_date:
            rides = rides.filter(
                created_at__date__lte=end_date
            )

        # Driver filtering
        driver_id = request.query_params.get("driver_id")

        if driver_id:
            rides = rides.filter(
                driver_id=driver_id
            )

        # Fare filtering
        min_fare = request.query_params.get("min_fare")
        max_fare = request.query_params.get("max_fare")

        if min_fare:
            rides = rides.filter(
                fare__gte=min_fare
            )

        if max_fare:
            rides = rides.filter(
                fare__lte=max_fare
            )

        rides = rides.order_by("-created_at")

        return Response({
            "count": rides.count(),
            "rides": RideSerializer(
                rides,
                many=True
            ).data
        })
class UserCompletedRidesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        rides = Ride.objects.filter(
            user=request.user,
            status=RideStatus.COMPLETED
        ).select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        )

        # Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            rides = rides.filter(
                created_at__date__gte=start_date
            )

        if end_date:
            rides = rides.filter(
                created_at__date__lte=end_date
            )

        # Driver filtering
        driver_id = request.query_params.get("driver_id")

        if driver_id:
            rides = rides.filter(
                driver_id=driver_id
            )

        # Fare filtering
        min_fare = request.query_params.get("min_fare")
        max_fare = request.query_params.get("max_fare")

        if min_fare:
            rides = rides.filter(
                fare__gte=min_fare
            )

        if max_fare:
            rides = rides.filter(
                fare__lte=max_fare
            )

        rides = rides.order_by("-created_at")

        return Response({
            "count": rides.count(),
            "rides": RideSerializer(
                rides,
                many=True
            ).data
        })   
class UserCancelledRidesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        rides = Ride.objects.filter(
            user=request.user,
            status=RideStatus.CANCELLED
        ).select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        )

        # Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            rides = rides.filter(
                created_at__date__gte=start_date
            )

        if end_date:
            rides = rides.filter(
                created_at__date__lte=end_date
            )

        # Driver filtering
        driver_id = request.query_params.get("driver_id")

        if driver_id:
            rides = rides.filter(
                driver_id=driver_id
            )

        # Fare filtering
        min_fare = request.query_params.get("min_fare")
        max_fare = request.query_params.get("max_fare")

        if min_fare:
            rides = rides.filter(
                fare__gte=min_fare
            )

        if max_fare:
            rides = rides.filter(
                fare__lte=max_fare
            )

        rides = rides.order_by("-created_at")

        return Response({
            "count": rides.count(),
            "rides": RideSerializer(
                rides,
                many=True
            ).data
        })
class DriverRideHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rides = Ride.objects.filter(
            driver__user=request.user
        ).select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        ).order_by("-created_at")

        return Response({
            "count": rides.count(),
            "rides": RideSerializer(
                rides,
                many=True
            ).data
        })
class RideHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        rides = get_ride_history(
            request.user,
            request.query_params
        )

        paginator = RideHistoryPagination()

        page = paginator.paginate_queryset(
            rides,
            request
        )

        serializer = RideSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)
class RideHistoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50    
class DailyRideCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        count = Ride.objects.filter(
            user=request.user,
            created_at__date=today
        ).count()

        return Response({
            "date": str(today),
            "daily_ride_count": count
        })
class TotalCompletedRidesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Ride.objects.filter(
            user=request.user,
            status="COMPLETED"
        ).count()

        return Response({
            "total_completed_rides": count
        })
class DriverTotalFareAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = Ride.objects.filter(
            driver__user=request.user,
            status="COMPLETED"
        ).aggregate(
            total_fare=Sum("fare")
        )

        return Response({
            "total_fare_earned": result["total_fare"] or 0
        })
class RideAggregationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        result = Ride.objects.aggregate(
            total_rides=Count("id"),
            completed_rides=Count(
                "id",
                filter=Q(status="COMPLETED")
            ),
            cancelled_rides=Count(
                "id",
                filter=Q(status="CANCELLED")
            ),
            average_fare=Avg("fare"),
            maximum_fare=Max("fare"),
            minimum_fare=Min("fare"),
            total_driver_earnings=Sum(
                "fare",
                filter=Q(
                    status="COMPLETED",
                    driver__isnull=False
                )
            )
        )

        return Response({
            "total_rides": result["total_rides"],
            "completed_rides": result["completed_rides"],
            "cancelled_rides": result["cancelled_rides"],
            "average_fare": result["average_fare"],
            "maximum_fare": result["maximum_fare"],
            "minimum_fare": result["minimum_fare"],
            "total_driver_earnings": result["total_driver_earnings"] or 0,
        })

class AdvancedQuerySetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 1. filter()
        completed_rides = Ride.objects.filter(
            status=RideStatus.COMPLETED
        )

        # 2. exclude()
        non_cancelled_rides = Ride.objects.exclude(
            status=RideStatus.CANCELLED
        )

        # 3. Q()
        completed_or_cancelled = Ride.objects.filter(
            Q(status=RideStatus.COMPLETED) |
            Q(status=RideStatus.CANCELLED)
        )

        # 4. F()
        rides_with_updated_time = Ride.objects.filter(
            updated_at__gt=F("created_at")
        )

        # 5. annotate()
        rides_by_status = Ride.objects.values(
            "status"
        ).annotate(
            ride_count=Count("id")
        )

        # 6. aggregate()
        fare_summary = Ride.objects.aggregate(
            total_fare=Sum("fare"),
            average_fare=Avg("fare"),
            maximum_fare=Max("fare"),
            minimum_fare=Min("fare")
        )

        # 7. values()
        ride_values = Ride.objects.values(
            "id",
            "status",
            "fare"
        )[:10]

        # 8. values_list()
        ride_ids = Ride.objects.values_list(
            "id",
            flat=True
        )[:10]

        # 9. exists()
        has_completed_rides = Ride.objects.filter(
            status=RideStatus.COMPLETED
        ).exists()

        # 10. distinct()
        distinct_statuses = Ride.objects.values(
            "status"
        ).distinct()

        return Response({
            "filter_count": completed_rides.count(),

            "exclude_count": non_cancelled_rides.count(),

            "q_count": completed_or_cancelled.count(),

            "f_count": rides_with_updated_time.count(),

            "annotate": list(rides_by_status),

            "aggregate": {
                "total_fare": fare_summary["total_fare"] or 0,
                "average_fare": fare_summary["average_fare"],
                "maximum_fare": fare_summary["maximum_fare"],
                "minimum_fare": fare_summary["minimum_fare"],
            },

            "values": list(ride_values),

            "values_list": [
                str(ride_id)
                for ride_id in ride_ids
            ],

            "exists": has_completed_rides,

            "distinct": list(distinct_statuses),
        })
    
class SlowRideListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Clear previous query information
        reset_queries()

        # Deliberately slow QuerySet
        rides = Ride.objects.all()

        for ride in rides:

            print(
                ride.user.email,
                ride.driver,
                ride.vehicle,
                ride.ride_type
            )

        query_count = len(
            connection.queries
        )

        print(
            "Slow API SQL queries:",
            query_count
        )

        return Response(
            {
                "message": "Slow API executed",
                "query_count": query_count
            },
            status=status.HTTP_200_OK
        )

class OptimizedRideListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Clear previous query information
        reset_queries()

        # Optimize ForeignKey relationships
        rides = Ride.objects.select_related(
            'user',
            'driver',
            'vehicle',
            'ride_type'
        )

        for ride in rides:

            print(
                ride.user.email,
                ride.driver,
                ride.vehicle,
                ride.ride_type
            )

        query_count = len(
            connection.queries
        )

        print(
            "Optimized API SQL queries:",
            query_count
        )

        return Response(
            {
                "message": "Optimized API executed",
                "query_count": query_count
            },
            status=status.HTTP_200_OK
        )

class DriverVehicleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Clear previous query information
        reset_queries()

        # Optimize reverse ForeignKey relationship
        drivers = DriverProfile.objects.prefetch_related(
            'vehicles'
        )

        for driver in drivers:

            print(
                driver.user.email
            )

            for vehicle in driver.vehicles.all():
                print(
                    vehicle.vehicle_number
                )

        query_count = len(
            connection.queries
        )

        print(
            "Prefetch API SQL queries:",
            query_count
        )

        return Response(
            {
                "message": "Driver vehicles fetched",
                "query_count": query_count
            },
            status=status.HTTP_200_OK
        )
class RideIndexPerformanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        query = Ride.objects.filter(
            user=request.user
        ).order_by("-created_at")

        execution_plan = query.explain(
            analyze=False
        )

        return Response({
            "query": str(query.query),
            "execution_plan": execution_plan
        })
class AdvancedRideFilterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        rides = Ride.objects.select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        )

        # Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            rides = rides.filter(
                created_at__date__gte=start_date
            )

        if end_date:
            rides = rides.filter(
                created_at__date__lte=end_date
            )

        # Status filtering
        status_value = request.query_params.get("status")

        if status_value:
            rides = rides.filter(
                status=status_value
            )

        # Driver filtering
        driver_id = request.query_params.get("driver_id")

        if driver_id:
            rides = rides.filter(
                driver_id=driver_id
            )

        # Fare range filtering
        min_fare = request.query_params.get("min_fare")
        max_fare = request.query_params.get("max_fare")

        if min_fare:
            rides = rides.filter(
                fare__gte=min_fare
            )

        if max_fare:
            rides = rides.filter(
                fare__lte=max_fare
            )

        # Ordering
        ordering = request.query_params.get(
            "ordering",
            "-created_at"
        )

        allowed_ordering_fields = [
            "created_at",
            "-created_at",
            "fare",
            "-fare",
            "status",
            "-status",
        ]

        if ordering in allowed_ordering_fields:
            rides = rides.order_by(ordering)
        else:
            rides = rides.order_by("-created_at")

        return Response(
            {
                "count": rides.count(),
                "results": RideSerializer(
                    rides,
                    many=True
                ).data
            },
            status=status.HTTP_200_OK
        )
class RideListCreateAPIView(generics.ListCreateAPIView):
    queryset = Ride.objects.select_related(
        "user",
        "driver",
        "vehicle",
        "ride_type"
    ).order_by("-created_at")

    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [RideCreationThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return success_response(
            "Ride created successfully",
            serializer.data,
            status.HTTP_201_CREATED
        )

class LargeDatasetPerformanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        reset_queries()

        start_time = time.perf_counter()

        rides = Ride.objects.select_related(
            "user",
            "driver",
            "vehicle",
            "ride_type"
        ).order_by("-created_at")

        # Force QuerySet evaluation
        list(rides[:20])

        end_time = time.perf_counter()

        response_time = (
            end_time - start_time
        ) * 1000

        query_count = len(connection.queries)

        return Response({
            "total_rides": Ride.objects.count(),
            "response_time_ms": round(
                response_time,
                2
            ),
            "database_queries": query_count,
            "page_size_tested": 20
        })
class DriverLocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver = get_object_or_404(
            DriverProfile,
            user=request.user
        )

        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude is None or longitude is None:
            return Response(
                {
                    "error": "Latitude and longitude are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
             return Response(
        {"error": "Latitude and longitude must be valid numbers."},
        status=status.HTTP_400_BAD_REQUEST
    )

        if not -90 <= latitude <= 90:
            return Response(
        {"error": "Latitude must be between -90 and 90."},
        status=status.HTTP_400_BAD_REQUEST
    )

        if not -180 <= longitude <= 180:
            return Response(
        {"error": "Longitude must be between -180 and 180."},
        status=status.HTTP_400_BAD_REQUEST
    )

        location, created = DriverLocation.objects.update_or_create(
            driver=driver,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
                "availability_status": DriverLocation.AvailabilityStatus.ONLINE
            }
        )

        return Response(
            {
                "message": "Driver location updated successfully.",
                "latitude": location.latitude,
                "longitude": location.longitude,
                "availability_status": location.availability_status,
                "last_updated": location.last_updated
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class NearbyDriverAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        radius = request.query_params.get("radius")

        if latitude is None or longitude is None or radius is None:
            return Response(
                {
                    "error": "latitude, longitude and radius are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except (ValueError, TypeError):
            return Response(
                {
                    "error": (
                        "latitude, longitude and radius "
                        "must be valid numbers."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if radius <= 0:
            return error_response(
        "radius must be greater than 0.",
        status_code=status.HTTP_400_BAD_REQUEST
    )

        drivers = find_nearby_drivers(
            latitude,
            longitude,
            radius
        )

        return Response(
            {
                "count": len(drivers),
                "drivers": drivers
            },
            status=status.HTTP_200_OK
        )
class DriverLocationUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        try:
            driver = request.user.driver_profile

        except DriverProfile.DoesNotExist:
            return Response(
                {"message": "Driver profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DriverLocationSerializer(
            driver,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        driver = update_driver_location(
            driver,
            serializer.validated_data["latitude"],
            serializer.validated_data["longitude"]
        )

        return success_response(
           "Driver location updated successfully.",
          {
             "latitude": driver.latitude,
             "longitude": driver.longitude,
          },
    status.HTTP_200_OK
)    
            


class DriverCacheBenchmarkAPIView(APIView):

    def get(self, request):
        reset_queries()

        start_time = time.perf_counter()

        drivers,cache_hit = find_nearby_drivers()

        response_time = (time.perf_counter() - start_time) * 1000
        cache_miss= not cache_hit

        return Response({
            "response_time_ms": round(response_time, 2),
            "database_queries": len(connection.queries),
            "cache_hit" :cache_hit,
            "cache_miss" :cache_miss,           
            "drivers_count": len(drivers),
        })
class VehicleTypeListAPIView(APIView):

    def get(self, request):

        cache_key = "vehicle_types"

        # Check Redis cache
        cached_vehicle_types = cache.get(cache_key)

        if cached_vehicle_types is not None:
            print("Vehicle Types: CACHE HIT")

            return Response({
                "vehicle_types": cached_vehicle_types
            })

        # Cache miss → get data from database
        print("Vehicle Types: CACHE MISS")

        vehicle_types = list(
            VehicleType.objects.values(
                "id",
                "name"
            )
        )

        # Store data in Redis for 1 hour
        cache.set(
            cache_key,
            vehicle_types,
            timeout=3600
        )

        return Response({
            "vehicle_types": vehicle_types
        })
    def post(self, request):

        name = request.data.get("name")

        if not name:
            return Response(
                {"error": "name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle_type = VehicleType.objects.create(
            name=name
        )

        # Invalidate Redis cache
        cache.delete("vehicle_types")

        return Response(
            {
                "message": "Vehicle type created successfully.",
                "id": str(vehicle_type.id),
                "name": vehicle_type.name
            },
            status=status.HTTP_201_CREATED
        )