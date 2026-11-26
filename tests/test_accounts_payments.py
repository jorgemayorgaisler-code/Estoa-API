import unittest
from unittest.mock import patch
from accounts_payments import create_pending_subscription, provider_request

class PaymentTests(unittest.TestCase):
    @patch("accounts_payments.provider_request")
    @patch.dict("os.environ",{"ESTOA_MP_BACK_URL":"https://example.test/return"})
    def test_price(self, request):
        create_pending_subscription("account-test","payer@example.test")
        path,payload=request.call_args.args
        self.assertEqual(path,"/preapproval")
        self.assertEqual(payload["auto_recurring"]["transaction_amount"],990)
        self.assertEqual(payload["auto_recurring"]["currency_id"],"CLP")
        self.assertEqual(payload["status"],"pending")

    @patch.dict("os.environ",{"ESTOA_MP_MODE":"production","ESTOA_MP_TEST_ACCESS_TOKEN":"TEST-example"})
    def test_production_blocked(self):
        with self.assertRaises(RuntimeError):
            provider_request("/preapproval")
