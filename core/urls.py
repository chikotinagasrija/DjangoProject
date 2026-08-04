from django.urls import path
from .api import welcome_api

urlpatterns = [
    path('welcome/', welcome_api),
]