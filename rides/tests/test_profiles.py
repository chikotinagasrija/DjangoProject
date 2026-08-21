from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import UserProfile


class ProfileTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="profile@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )

    def test_create_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
            phone_number="9876543210",
            gender="Male",
            city="Hyderabad",
            state="Telangana",
            country="India",
            pincode="500001",
            bio="Test profile"
        )

        self.assertEqual(
            profile.user,
            self.user
        )

        self.assertEqual(
            profile.phone_number,
            "9876543210"
        )

        self.assertEqual(
            profile.city,
            "Hyderabad"
        )

    def test_profile_default_not_deleted(self):
        profile = UserProfile.objects.create(
            user=self.user
        )

        self.assertFalse(
            profile.is_deleted
        )

    def test_update_profile(self):
        profile = UserProfile.objects.create(
            user=self.user
        )

        profile.city = "Bengaluru"
        profile.phone_number = "9999999999"
        profile.save()

        profile.refresh_from_db()

        self.assertEqual(
            profile.city,
            "Bengaluru"
        )

        self.assertEqual(
            profile.phone_number,
            "9999999999"
        )

    def test_profile_one_to_one_user(self):
        profile = UserProfile.objects.create(
            user=self.user
        )

        self.assertEqual(
            self.user.profile,
            profile
        )