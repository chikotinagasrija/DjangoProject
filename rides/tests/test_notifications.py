from django.test import TestCase
from django.contrib.auth import get_user_model

from common.models import Notification


class NotificationTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="notification@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Ride Accepted",
            message="Your ride has been accepted.",
            notification_type="RIDE",
            event_key="ride_123_accepted"
        )

        self.assertEqual(
            notification.user,
            self.user
        )

        self.assertEqual(
            notification.title,
            "Ride Accepted"
        )

        self.assertEqual(
            notification.notification_type,
            "RIDE"
        )

    def test_notification_unread_by_default(self):
        notification = Notification.objects.create(
            user=self.user,
            title="New Ride",
            message="You have a new ride.",
            notification_type="RIDE",
            event_key="ride_456"
        )

        self.assertFalse(
            notification.is_read
        )

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Payment",
            message="Payment completed.",
            notification_type="PAYMENT",
            event_key="payment_123"
        )

        notification.is_read = True
        notification.save()

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

    def test_notification_belongs_to_user(self):
        notification = Notification.objects.create(
            user=self.user,
            title="System Update",
            message="System updated successfully.",
            notification_type="SYSTEM",
            event_key="system_123"
        )

        self.assertEqual(
            notification.user.email,
            "notification@test.com"
        )