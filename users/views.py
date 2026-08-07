import profile

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser, UserProfile
from django.contrib.auth.models import Group
from .permissions import IsAdminUserRole
import logging
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ProfileImageSerializer
)
logger = logging.getLogger(__name__)



# Register API
class RegisterAPIView(APIView):

    def post(self, request):

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully",
                    "email": user.email
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Login API
class LoginAPIView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )


# Basic User Profile API
class ProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.select_related("user").get(user=request.user)
            print("Query Count:", len(connection.queries))

            user = profile.user

            logger.info(f"Profile viewed by {user.email}")

            return Response(
                {
                    "id": str(user.id),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(str(e))
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            profile = UserProfile.objects.select_related("user").get(user=request.user)

            serializer = UserProfileSerializer(
                profile,
                data=request.data
            )

            if serializer.is_valid():
                serializer.save(updated_by=request.user)

                logger.info(f"Profile updated by {request.user.email}")

                return Response(serializer.data, status=status.HTTP_200_OK)

            logger.error(serializer.errors)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(str(e))
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# Create Profile API
class CreateProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if UserProfile.objects.filter(user=request.user).exists():

            return Response(
                {
                    "error": "Profile already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserProfileSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# View Profile API
class ViewProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# Update Profile API
class UpdateProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save(updated_by=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Delete Profile API
class DeleteProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        profile = UserProfile.objects.get(
            user=request.user
        )

        profile.is_deleted = True
        profile.save()

        return Response(
            {
                "message": "Profile deleted successfully"
            },
            status=status.HTTP_200_OK
        )


# Upload Profile Image API
class UploadProfileImageAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        serializer = ProfileImageSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message": "Profile image uploaded successfully",
                    "image": serializer.data["profile_picture"]
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Change Password API
class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        current_password = request.data.get(
            "current_password"
        )

        new_password = request.data.get(
            "new_password"
        )


        if not user.check_password(current_password):

            return Response(
                {
                    "error": "Current password is incorrect"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        if len(new_password) < 8:

            return Response(
                {
                    "error": "New password must be at least 8 characters"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        user.set_password(new_password)

        user.save()


        return Response(
            {
                "message": "Password changed successfully"
            },
            status=status.HTTP_200_OK
        )


# Logout API
class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)

            token.blacklist()


            return Response(
                {
                    "message": "Logout successful"
                },
                status=status.HTTP_205_RESET_CONTENT
            )


        except Exception:

            return Response(
                {
                    "error": "Invalid token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
class ProfileListAPIView(ListAPIView):

    queryset = UserProfile.objects.all()

    serializer_class = UserProfileSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "gender",
        "city",
        "state",
        "country",
    ]

    search_fields = [
        "user__first_name",
        "user__last_name",
        "city",
        "country",
    ]

    ordering_fields = [
        "city",
        "state",
        "country",
    ]

# Admin Only API
class AdminAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(
            {
                "message": "Welcome Admin"
            },
            status=status.HTTP_200_OK
        )
class RestoreProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = UserProfile.objects.get(user=request.user)

        profile.is_deleted = False
        profile.save()

        return Response(
            {
                "message": "Profile restored successfully"
            },
            status=status.HTTP_200_OK
        )    