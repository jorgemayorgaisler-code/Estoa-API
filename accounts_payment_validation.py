from decimal import Decimal, InvalidOperation

def validate_payment(payment, expected_id, expected_amount, expected_merchant):
    """Conservative evidence check; not sufficient to grant access."""
    if not expected_merchant or str(payment.get("id"))!=str(expected_id) or str(payment.get("collector_id"))!=str(expected_merchant):
        raise ValueError("Payment identity mismatch")
    if payment.get("currency_id")!="CLP" or payment.get("status")!="approved":
        raise ValueError("Payment not approved in CLP")
    try:
        amount=Decimal(str(payment.get("transaction_amount")))
        refunded=Decimal(str(payment.get("transaction_amount_refunded")))
        if not amount.is_finite() or not refunded.is_finite() or amount!=Decimal(expected_amount) or refunded!=0:
            raise ValueError("Payment amount or refund mismatch")
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc
    return True
