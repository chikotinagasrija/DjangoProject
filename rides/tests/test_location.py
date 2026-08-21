from django.test import TestCase
from django.contrib.auth import get_user_model

from rides.models import DriverProfile


class LocationTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="location@test.com",
            password="testpass123"
        )

    def test_driver_location(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL12345",
            latitude=17.3850,
            longitude=78.4867,
            is_active=True
        )

        self.assertEqual(
            float(driver.latitude),
            17.3850
        )

        self.assertEqual(
            float(driver.longitude),
            78.4867
        )

    def test_invalid_latitude(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL12346",
            latitude=200,
            longitude=78.4867,
            is_active=True
        )

        self.assertEqual(
            float(driver.latitude),
            200
        )