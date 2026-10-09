"""Offline payment foundation tests: never call Mercado Pago or charge a card."""
import os
import json
from io import BytesIO
import unittest
from unittest.mock import patch
from payments_mercadopago import (
    PaymentConfigurationError, create_subscription, premium_eligible,
    subscription_configured, fetch_subscription_status,
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


    def test_subscription_status_verified_remotely(self):
        class Response:
            def __enter__(self):
                return BytesIO(json.dumps({
                    "id": "preapproval-123", "status": "authorized",
                    "external_reference": "account-1"
                }).encode())
            def __exit__(self, *args):
                return False

        with patch.dict(os.environ, {"MERCADOPAGO_ACCESS_TOKEN": "test-token"}):
            with patch("payments_mercadopago.urlopen", return_value=Response()) as mocked:
                result = fetch_subscription_status("preapproval-123")
        self.assertTrue(result["premium_eligible"])
        self.assertEqual(result["external_reference"], "account-1")
        self.assertEqual(mocked.call_args.args[0].get_method(), "GET")

    def test_status_id_mismatch_never_activates(self):
        class Response:
            def __enter__(self):
                return BytesIO(b'{"id":"different","status":"authorized"}')
            def __exit__(self, *args):
                return False

        with patch.dict(os.environ, {"MERCADOPAGO_ACCESS_TOKEN": "test-token"}):
            with patch("payments_mercadopago.urlopen", return_value=Response()):
                with self.assertRaises(RuntimeError):
                    fetch_subscription_status("preapproval-123")

    def test_subscription_id_input_is_restricted(self):
        with patch.dict(os.environ, {"MERCADOPAGO_ACCESS_TOKEN": "test-token"}):
            with self.assertRaises(ValueError):
                fetch_subscription_status("../invalid")

if __name__ == "__main__":
    unittest.main()
