from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import Group

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import CustomUser, UserProfile



class AuthenticationTests(APITestCase):

    def setUp(self):
        self.email = "test@example.com"
        self.password = "Test@12345"

        self.user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email=self.email,
            password=self.password
        )

        # Profile is required by ProfileAPIView
        self.profile = UserProfile.objects.create(
            user=self.user
        )

    # --------------------------------------------------
    # 1. Registration
    # --------------------------------------------------
    def test_registration(self):
        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "password": "Test@12345"
        }

        response = self.client.post(
            "/api/v1/users/register/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            CustomUser.objects.filter(
                email="newuser@example.com"
            ).exists()
        )

    # --------------------------------------------------
    # 2. Login
    # --------------------------------------------------
    def test_login(self):
        data = {
            "email": self.email,
            "password": self.password
        }

        response = self.client.post(
            "/api/v1/users/login/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # --------------------------------------------------
    # 3. Invalid Credentials
    # --------------------------------------------------
    def test_invalid_login(self):
        data = {
            "email": self.email,
            "password": "WrongPassword123"
        }

        response = self.client.post(
            "/api/v1/users/login/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 401)

    # --------------------------------------------------
    # 4. Logout
    # --------------------------------------------------
    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/v1/users/logout/",
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(response.status_code, 205)

    # --------------------------------------------------
    # 5. Password Change
    # --------------------------------------------------
    def test_password_change(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "current_password": self.password,
            "new_password": "NewPassword@123"
        }

        response = self.client.post(
            "/api/v1/users/change-password/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword@123"
            )
        )

    # --------------------------------------------------
    # 6. Password Change - Wrong Current Password
    # --------------------------------------------------
    def test_password_change_wrong_password(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "current_password": "WrongPassword123",
            "new_password": "NewPassword@123"
        }

        response = self.client.post(
            "/api/v1/users/change-password/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------
    # 7. Expired Access Token
    # --------------------------------------------------
    def test_expired_token(self):
        token = AccessToken.for_user(self.user)

        # Make the access token expired
        token["exp"] = int(
            (
                timezone.now() - timedelta(minutes=1)
            ).timestamp()
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(token)}"
        )

        response = self.client.get(
            "/api/v1/users/profile/"
        )

        self.assertEqual(response.status_code, 401)

    # --------------------------------------------------
    # 8. Token Refresh
    # --------------------------------------------------
    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/v1/users/token/refresh/",
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "access",
            response.data
        )
class PermissionTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            first_name="Test",
            last_name="User",
            email="user@example.com",
            password="Test@12345"
        )

        self.admin = CustomUser.objects.create_superuser(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="Admin@12345"
        )
        admin_group, created = Group.objects.get_or_create(
            name="Admin"
)

        self.admin.groups.add(admin_group)

    # Anonymous user
    def test_anonymous_cannot_access_admin_api(self):
        response = self.client.get(
            "/api/v1/users/admin-api/"
        )

        self.assertEqual(response.status_code, 401)

    # Normal authenticated user
    def test_normal_user_cannot_access_admin_api(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/v1/users/admin-api/"
        )

        self.assertEqual(response.status_code, 403)

    # Admin user
    def test_admin_can_access_admin_api(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/v1/users/admin-api/"
        )

        self.assertEqual(response.status_code, 200)