from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import DriverProfile, Vehicle,Ride,RideStatus,ALLOWED_RIDE_TRANSITIONS
from rest_framework.permissions import IsAuthenticated
from .serializers import DriverProfileSerializer, VehicleSerializer,DriverNestedSerializer,RideSerializer,RideStatusSerializer
from .permissions import IsAdminOrOwnVehicle, IsAdminOrSelfDriver

class DriverListCreateAPIView(generics.ListCreateAPIView):
    queryset = DriverProfile.objects.all()
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
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    

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
    queryset = DriverProfile.objects.all()
    serializer_class = DriverNestedSerializer

class RideCreateAPIView(generics.CreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RideDetailAPIView(generics.RetrieveAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]  

class RideStatusAPIView(generics.UpdateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideStatusSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        ride = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        current_status = ride.status

        allowed_statuses = ALLOWED_RIDE_TRANSITIONS.get(
            current_status, []
        )

        if new_status not in allowed_statuses:
            return Response(
                {
                    "error": (
                        f"Invalid status transition: "
                        f"{current_status} → {new_status}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ride.status = new_status
        ride.save()

        return Response(
            {
                "message": "Ride status updated successfully.",
                "ride_id": str(ride.id),
                "status": ride.status
            },
            status=status.HTTP_200_OK
        )  
class RideAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            driver = DriverProfile.objects.get(
                user=request.user
            )
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "User is not registered as a driver."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not driver.is_active:
            return Response(
                {"error": "Driver is not active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ride = Ride.objects.get(id=pk)
        except Ride.DoesNotExist:
            return Response(
                {"error": "Ride not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if ride.status != RideStatus.REQUESTED:
            return Response(
                {"error": "Ride is no longer available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        active_statuses = [
            RideStatus.ACCEPTED,
            RideStatus.DRIVER_ARRIVING,
            RideStatus.STARTED,
        ]

        if Ride.objects.filter(
            driver=driver,
            status__in=active_statuses
        ).exists():
            return Response(
                {"error": "Driver already has an active ride."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ride.driver = driver
        ride.status = RideStatus.ACCEPTED
        ride.save()

        return Response(
            {
                "message": "Ride accepted successfully.",
                "ride_id": str(ride.id),
                "driver": str(driver.id),
                "status": ride.status
            },
            status=status.HTTP_200_OK
        ) 
class RideCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            ride = Ride.objects.get(id=pk)
        except Ride.DoesNotExist:
            return Response(
                {
                    "error": "Ride not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        allowed_statuses = [
            RideStatus.REQUESTED,
            RideStatus.ACCEPTED,
            RideStatus.DRIVER_ARRIVING,
        ]

        if ride.status not in allowed_statuses:
            return Response(
                {
                    "error": "Ride cannot be cancelled in its current status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ride.status = RideStatus.CANCELLED
        ride.save()

        return Response(
            {
                "message": "Ride cancelled successfully.",
                "ride_id": str(ride.id),
                "status": ride.status
            },
            status=status.HTTP_200_OK
        )        
