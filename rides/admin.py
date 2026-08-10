from django.contrib import admin
from .models import DriverProfile, Vehicle, VehicleType, Ride


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'license_number', 'rating', 'created_at')
    search_fields = ('license_number', 'user__email')
    ordering = ('-created_at',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'driver',
        'vehicle_type',
        'vehicle_number',
        'model',
        'created_at'
    )

    search_fields = (
        'vehicle_number',
        'model',
        'driver__license_number',
    )

    list_filter = (
        'vehicle_type',
    )

    ordering = ('-created_at',)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'driver',
        'vehicle',
        'status',
        'fare',
        'created_at',
    )

    search_fields = (
        'user__email',
        'driver__license_number',
        'vehicle__vehicle_number',
        'pickup_location',
        'drop_location',
    )

    list_filter = (
        'status',
        'created_at',
    )

    ordering = ('-created_at',)
