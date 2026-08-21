from django.test import TestCase
from django.contrib.auth import get_user_model


class AuthenticationTests(TestCase):

    def setUp(self):
        self.User = get_user_model()

    def test_user_registration(self):
        user = self.User.objects.create_user(
            email="testuser@test.com",
            password="testpass123"
        )

        self.assertEqual(user.email, "testuser@test.com")
        self.assertTrue(
            user.check_password("testpass123")
        )

    def test_user_login_credentials(self):
        user = self.User.objects.create_user(
            email="login@test.com",
            password="testpass123"
        )

        self.assertTrue(
            user.check_password("testpass123")
        )

    def test_invalid_password(self):
        user = self.User.objects.create_user(
            email="invalid@test.com",
            password="testpass123"
        )

        self.assertFalse(
            user.check_password("wrongpassword")
        )