from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import DriverProfile, Vehicle,Ride
from rest_framework.permissions import IsAuthenticated
from .serializers import DriverProfileSerializer, VehicleSerializer,DriverNestedSerializer,RideSerializer,RideStatusSerializer
from .permissions import IsAdminOrOwnVehicle, IsAdminOrSelfDriver
from django.shortcuts import get_object_or_404
from .services.fare_service import calculate_fare


from .services.ride_service import (
    update_ride_status,
    accept_ride,
    cancel_ride,
)

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

class RideCreateAPIView(generics.CreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RideDetailAPIView(generics.RetrieveAPIView):
    queryset = Ride.objects.select_related('user', 'driver', 'vehicle', 'ride_type')
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated] 

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
                {"error": "Invalid distance or duration."},
                status=status.HTTP_400_BAD_REQUEST
            )

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