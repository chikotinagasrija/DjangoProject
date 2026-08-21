from django.test import TestCase
from django.contrib.auth import get_user_model

from rides.models import DriverProfile


class DriverTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="driver@test.com",
            password="testpass123"
        )

    def test_create_driver(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL12345",
            is_active=True
        )

        self.assertEqual(
            driver.license_number,
            "DL12345"
        )

        self.assertTrue(
            driver.is_active
        )

    def test_driver_is_active(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL67890",
            is_active=True
        )

        self.assertTrue(driver.is_active)

    def test_driver_inactive(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL99999",
            is_active=False
        )

        self.assertFalse(driver.is_active)