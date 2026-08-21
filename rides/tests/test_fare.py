from django.test import TestCase
from rides.services.fare_service import calculate_fare


class FareTests(TestCase):

    def test_valid_fare(self):
        result = calculate_fare(
            distance_km=10,
            duration_minutes=20
        )

        self.assertEqual(
            result["total"],
            150
        )

    def test_zero_distance(self):
        result = calculate_fare(
            distance_km=0,
            duration_minutes=10
        )

        self.assertIsNotNone(result)

    def test_invalid_distance(self):
        with self.assertRaises((ValueError, TypeError)):
            calculate_fare(
                distance_km=-10,
                duration_minutes=20
            )