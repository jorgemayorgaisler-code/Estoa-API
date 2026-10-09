"""Offline payment foundation tests: never call Mercado Pago or charge a card."""
import os
import unittest
from unittest.mock import patch
from payments_mercadopago import (
    PaymentConfigurationError, create_subscription, premium_eligible,
    subscription_configured,
)


class PaymentFoundationTests(unittest.TestCase):
    def test_payments_disabled_without_secrets(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(subscription_configured())
            with self.assertRaises(PaymentConfigurationError):
                create_subscription("test@example.com", "user-1")

    def test_no_client_claim_can_grant_access(self):
        for status in ("pending", "paused", "canceled", None):
            self.assertFalse(premium_eligible({"status": status}))
        self.assertFalse(premium_eligible(None))
        self.assertTrue(premium_eligible({"status": "authorized"}))

    def test_invalid_price_rejected_without_network(self):
        with patch.dict(os.environ, {"MERCADOPAGO_ACCESS_TOKEN": "placeholder",
                                     "ESTOA_PREMIUM_PRICE_CLP": "0"}, clear=True):
            with self.assertRaises(PaymentConfigurationError):
                create_subscription("test@example.com", "user-1")


if __name__ == "__main__":
    unittest.main()
