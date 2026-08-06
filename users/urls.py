from django.urls import path
from .views import (
    ProfileListAPIView,
    RegisterAPIView,
    LoginAPIView,
    ProfileAPIView,
    ChangePasswordAPIView,
    LogoutAPIView,
    CreateProfileAPIView,
    ViewProfileAPIView,
    UpdateProfileAPIView,
    DeleteProfileAPIView,
    UploadProfileImageAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("profile/", ProfileAPIView.as_view()),
    path("change-password/", ChangePasswordAPIView.as_view()),
    path("logout/", LogoutAPIView.as_view()),

    # Profile CRUD APIs
    path("profile/create/", CreateProfileAPIView.as_view()),
    path("profile/view/", ViewProfileAPIView.as_view()),
    path("profile/update/", UpdateProfileAPIView.as_view()),
    path("profile/delete/", DeleteProfileAPIView.as_view()),
    path("profile/upload-image/", UploadProfileImageAPIView.as_view()),
    path(
    "profiles/",
    ProfileListAPIView.as_view(),
    name="profile-list"
), # New endpoint for listing profiles
    
]   