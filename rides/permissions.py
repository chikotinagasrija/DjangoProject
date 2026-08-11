from rest_framework.permissions import BasePermission


class IsAdminOrOwnVehicle(BasePermission):

    def has_object_permission(self, request, view, obj):

        # Admin can manage all vehicles
        if request.user.is_staff:
            return True

        # Driver can manage only their own vehicle
        if obj.driver.user == request.user:
            return True

        # Normal users and other drivers are denied
        return False
class IsAdminOrSelfDriver(BasePermission):

    def has_object_permission(self, request, view, obj):

        # Admin can manage all drivers
        if request.user.is_staff:
            return True

        # Driver can manage only their own driver profile
        if obj.user == request.user:
            return True

        # Normal users and other drivers are denied
        return False
