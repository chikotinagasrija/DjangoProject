import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rides.models import BookingStatus

from .models import Payment, PaymentStatus
from rides.models import BookingStatus
from .services import process_mock_payment
from .serializers import PaymentInitiateSerializer, PaymentSerializer, PaymentWebhookSerializer
from rides.services.ride_service import update_booking_status
from django.db import transaction
from common.tasks import ride_notification



class PaymentInitiateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]
        amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data["payment_method"]

        # Prevent multiple pending payments for the same booking
        existing_payment = Payment.objects.filter(
            booking=booking,
            status=PaymentStatus.PENDING,
        ).first()

        if existing_payment:
            return Response(
                PaymentSerializer(existing_payment).data,
                status=status.HTTP_200_OK,
            )

        transaction_id = f"MOCK-TXN-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            transaction_id=transaction_id,
            status=PaymentStatus.PENDING,
            payment_method=payment_method,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
class MockPaymentProcessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get("payment_id")
        result = request.data.get("result", "SUCCESS")

        if not payment_id:
            return Response(
                {"detail": "payment_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(
                id=payment_id,
                booking__user=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            payment = process_mock_payment(
                payment,
                result=result,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )
class PaymentWebhookAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PaymentWebhookSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        payment = serializer.validated_data["payment"]
        new_status = serializer.validated_data["status"]

        payment.status = new_status
        payment.save(update_fields=["status"])

        if new_status == PaymentStatus.SUCCESS:
            update_booking_status(
                payment.booking,
                BookingStatus.CONFIRMED,
            )
            transaction.on_commit(
               lambda: ride_notification.delay(
               payment.booking.user.id,
              "Payment Successful",
              "Your payment was successful.",
              f"{payment.booking.id}:PAYMENT_SUCCESS",
    )
)

        elif new_status == PaymentStatus.FAILED:
            update_booking_status(
                payment.booking,
                BookingStatus.PAYMENT_FAILED,
            )

        return Response(
            {
                "message": "Payment confirmation processed successfully.",
                "payment": PaymentSerializer(payment).data,
            },
            status=status.HTTP_200_OK,
        )