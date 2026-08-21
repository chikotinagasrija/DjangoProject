from django.core.cache import cache
from rides.models import DriverProfile
CACHE_KEY="nearby_drivers"


def get_nearby_drivers():
    

    # Cache Hit
    cached_drivers = cache.get(CACHE_KEY)

    if cached_drivers is not None:
        print("CACHE HIT")
        return cached_drivers,True

    # Cache Miss
    print("CACHE MISS")

    drivers = list(
        DriverProfile.objects.filter(
            is_active=True
        ).values(
            "id",
            "latitude",
            "longitude"
        )
    )

    # Cache for 30 seconds
    cache.set(CACHE_KEY, drivers, timeout=30)

    return drivers, False

def invalidate_driver_cache():
    cache.delete(CACHE_KEY)
    print("DRIVER CACHE INVALIDATED")