from rest_framework.throttling import UserRateThrottle


class RideCreationThrottle(UserRateThrottle):
    scope = "ride_creation"