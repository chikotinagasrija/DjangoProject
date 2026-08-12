from rest_framework import serializers
from .models import DriverProfile
from .models import Vehicle, VehicleType
from .models import Ride, RideStatus


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

    def validate_vehicle_number(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Vehicle registration number is required."
            )
        queryset = Vehicle.objects.filter(vehicle_number=value)

        if self.instance:
          queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
          raise serializers.ValidationError(
            "Vehicle registration number already exists."
        )


        return value

    def validate_driver(self, value):
        if not DriverProfile.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Invalid driver ID."
            )

        return value

    def validate_vehicle_type(self, value):
        if not VehicleType.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Invalid vehicle type ID."
            )

        return value


class NestedVehicleSerializer(serializers.ModelSerializer):
    type = serializers.CharField(
        source='vehicle_type.name',
        read_only=True
    )
    registration_number = serializers.CharField(
        source='vehicle_number',
        read_only=True
    )

    class Meta:
        model = Vehicle
        fields = ['type', 'registration_number']


class DriverNestedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='user.email',
        read_only=True
    )
    vehicle = NestedVehicleSerializer(
        source='vehicles.first',
        read_only=True
    )

    class Meta:
        model = DriverProfile
        fields = ['id', 'name', 'vehicle']


class RideSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ride
        fields = [
            "id",
            "user",
            "driver",
            "vehicle",
            "pickup_location",
            "drop_location",
            "fare",
            "ride_type",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "driver",
            "vehicle",
            "fare",
            "status",
            "created_at",
        ]        
    def validate_pickup_location(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Pickup location is required."
            )

        return value

    def validate_drop_location(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Drop location is required."
            )

        return value

    def validate(self, data):
        pickup = data.get("pickup_location")
        drop = data.get("drop_location")

        if pickup and drop:
            if pickup.strip().lower() == drop.strip().lower():
                raise serializers.ValidationError(
                    "Pickup and drop locations must be different."
                )

        user = self.context["request"].user

        active_statuses = [
            RideStatus.REQUESTED,
            RideStatus.ACCEPTED,
            RideStatus.DRIVER_ARRIVING,
            RideStatus.STARTED,
        ]

        if Ride.objects.filter(
            user=user,
            status__in=active_statuses
        ).exists():
            raise serializers.ValidationError(
                "You already have an active ride."
            )

        return data 
    
class RideStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=RideStatus.choices
    )