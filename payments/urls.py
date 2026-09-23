from django.urls import path

from .views import (
    PaymentInitiateAPIView,
    MockPaymentProcessAPIView,
    PaymentWebhookAPIView,
)



urlpatterns = [
    path(
        "initiate/",
        PaymentInitiateAPIView.as_view(),
        name="payment-initiate",
    ),
    path(
        "mock/process/",
        MockPaymentProcessAPIView.as_view(),
        name="mock-payment-process",
    ),
    path(
        "webhook/",
        PaymentWebhookAPIView.as_view(),
        name="payment-webhook",
    ),
]