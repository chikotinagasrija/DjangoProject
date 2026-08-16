from decimal import Decimal


def calculate_fare(
    distance_km,
    duration_minutes,
    base_fare=Decimal("40.00"),
    per_km_rate=Decimal("8.00"),
    per_minute_rate=Decimal("1.00"),
    surge_charge=Decimal("10.00"),
):
    distance_fare = Decimal(str(distance_km)) * per_km_rate
    time_fare = Decimal(str(duration_minutes)) * per_minute_rate

    total = (
        base_fare
        + distance_fare
        + time_fare
        + surge_charge
    )

    return {
        "base_fare": base_fare,
        "distance_fare": distance_fare,
        "time_fare": time_fare,
        "surge": surge_charge,
        "total": total,
    }
