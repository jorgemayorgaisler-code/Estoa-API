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
