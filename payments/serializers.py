from decimal import Decimal

from rest_framework import serializers

from rides.models import Ride
from .models import Payment, PaymentStatus


class PaymentInitiateSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    payment_method = serializers.CharField(
        max_length=50,
        default="MOCK",
    )

    def validate(self, data):
        request = self.context["request"]

        try:
            booking = Ride.objects.get(id=data["booking_id"])
        except Ride.DoesNotExist:
            raise serializers.ValidationError(
                {"booking_id": "Booking does not exist."}
            )

        # Booking must belong to the logged-in customer
        if booking.user != request.user:
            raise serializers.ValidationError(
                {"booking_id": "You are not allowed to pay for this booking."}
            )

        # Validate amount against the actual ride fare
        if Decimal(data["amount"]) != booking.fare:
            raise serializers.ValidationError(
                {"amount": "Payment amount does not match the booking fare."}
            )

        # Cancelled/completed bookings cannot be paid
        if booking.status in ["CANCELLED", "COMPLETED"]:
            raise serializers.ValidationError(
                {"booking_id": "This booking is not payable."}
            )

        data["booking"] = booking
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "transaction_id",
            "status",
            "payment_method",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "status",
            "created_at",
        ]
class PaymentWebhookSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(
        choices=[
            PaymentStatus.SUCCESS,
            PaymentStatus.FAILED,
        ]
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def validate(self, data):
        try:
            payment = Payment.objects.get(
                transaction_id=data["transaction_id"]
            )
        except Payment.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "transaction_id": "Payment transaction does not exist."
                }
            )

        # Webhook can only process a pending payment
        if payment.status != PaymentStatus.PENDING:
            raise serializers.ValidationError(
                {
                    "status": (
                        f"Payment is already {payment.status} "
                        "and cannot be updated."
                    )
                }
            )

        # Validate webhook amount against the stored payment
        if data["amount"] != payment.amount:
            raise serializers.ValidationError(
                {
                    "amount": "Webhook amount does not match payment amount."
                }
            )

        data["payment"] = payment

        return data