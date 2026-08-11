from rest_framework import generics
from .models import DriverProfile, Vehicle
from .serializers import DriverProfileSerializer, VehicleSerializer,DriverNestedSerializer
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
