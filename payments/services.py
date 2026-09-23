from .models import Payment, PaymentStatus


def process_mock_payment(payment, result="SUCCESS"):
    """
    Simulate payment processing using a mock gateway.
    No real financial transaction is performed.
    """

    if payment.status != PaymentStatus.PENDING:
        raise ValueError("Only pending payments can be processed.")

    result = result.upper()

    if result not in {
        PaymentStatus.SUCCESS,
        PaymentStatus.FAILED,
    }:
        raise ValueError("Invalid mock payment result.")

    if result == PaymentStatus.SUCCESS:
        payment.status = PaymentStatus.SUCCESS
    else:
        payment.status = PaymentStatus.FAILED

    payment.save(update_fields=["status"])

    return payment