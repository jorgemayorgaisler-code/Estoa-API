"""Mercado Pago subscription foundation. No payments without explicit server configuration."""
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MP_API = "https://api.mercadopago.com"


class PaymentConfigurationError(RuntimeError):
    pass


def subscription_configured():
    return bool(os.getenv("MERCADOPAGO_ACCESS_TOKEN") and os.getenv("ESTOA_PREMIUM_PRICE_CLP"))


def _price():
    raw = os.getenv("ESTOA_PREMIUM_PRICE_CLP", "")
    if not raw.isdigit() or int(raw) <= 0:
        raise PaymentConfigurationError("Positive CLP premium price is not configured")
    return int(raw)


def create_subscription(email, reference):
    """Create pending subscription; returning a checkout URL never grants premium access."""
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise PaymentConfigurationError("Mercado Pago token is not configured")
    if not email or "@" not in email or not reference:
        raise ValueError("Valid payer email and user reference required")
    price = _price()
    payload = {
        "reason": "ESTOA Premium",
        "external_reference": str(reference),
        "payer_email": str(email),
        "back_url": "https://estoa-web.onrender.com/",
        "auto_recurring": {
            "frequency": 1, "frequency_type": "months",
            "transaction_amount": price, "currency_id": "CLP"
        },
        "status": "pending",
    }
    req = Request(
        MP_API + "/preapproval",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=15) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("Mercado Pago subscription request failed") from exc
    checkout = result.get("init_point")
    if not isinstance(checkout, str) or not checkout.startswith("https://"):
        raise RuntimeError("Mercado Pago did not return a secure checkout URL")
    return {"checkout_url": checkout, "subscription_id": result.get("id"),
            "premium_active": False}


def premium_eligible(subscription):
    """Only verified remote status is eligible; never trust browser redirects."""
    return bool(subscription and subscription.get("status") == "authorized")


def fetch_subscription_status(subscription_id):
    """Retrieve authoritative subscription status from Mercado Pago server-side."""
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise PaymentConfigurationError("Mercado Pago token is not configured")
    if not isinstance(subscription_id, str) or not subscription_id or not all(
        char.isalnum() or char in "-_" for char in subscription_id
    ):
        raise ValueError("Invalid subscription identifier")
    req = Request(
        MP_API + "/preapproval/" + subscription_id,
        headers={"Authorization": "Bearer " + token},
        method="GET",
    )
    try:
        with urlopen(req, timeout=15) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("Mercado Pago subscription verification failed") from exc
    if not isinstance(data, dict) or str(data.get("id")) != subscription_id:
        raise RuntimeError("Mercado Pago subscription identifier mismatch")
    return {
        "subscription_id": subscription_id,
        "status": data.get("status"),
        "external_reference": data.get("external_reference"),
        "premium_eligible": premium_eligible(data),
    }
