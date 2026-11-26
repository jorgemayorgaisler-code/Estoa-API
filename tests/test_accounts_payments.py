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

    @patch.dict("os.environ",{"ESTOA_MP_MODE":"sandbox","ESTOA_MP_TEST_ACCESS_TOKEN":"TEST-example"})
    @patch("accounts_payments.build_opener")
    def test_response_validation(self, opener):
        response=opener.return_value.open.return_value.__enter__.return_value
        for raw in (b"[]",b"x"*1048577):
            response.read.return_value=raw
            with self.assertRaises(ValueError):
                provider_request("/preapproval")
        response.read.return_value=b'{"id":"test"}'
        self.assertEqual(provider_request("/preapproval"),{"id":"test"})

    def test_redirect_rejected(self):
        from accounts_payments import NoRedirect
        from urllib.request import Request
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError):
            NoRedirect().redirect_request(Request("https://api.mercadopago.com/preapproval"),None,302,"redirect",{}, "https://example.test")

    @patch.dict("os.environ",{"ESTOA_MP_BACK_URL":"https://user:password@example.test"})
    def test_return_url_credentials_rejected(self):
        with self.assertRaises(RuntimeError):
            create_pending_subscription("account-test","payer@example.test")
