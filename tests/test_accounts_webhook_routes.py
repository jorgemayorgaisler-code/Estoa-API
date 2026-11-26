import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_webhook_routes import build_webhook_router

class WebhookRouteTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI()
        app.include_router(build_webhook_router())
        self.client=TestClient(app)
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"production","ESTOA_WEBHOOK_PREVIEW":"true"})
    def test_production_blocked(self):
        self.assertEqual(self.client.post("/payments/webhook?data.id=abc").status_code,404)
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"sandbox","ESTOA_WEBHOOK_PREVIEW":"true"})
    @patch("accounts_webhook_routes.receive_notification",return_value="duplicate")
    def test_duplicate_acknowledged(self,mock):
        self.assertEqual(self.client.post("/payments/webhook?data.id=abc").status_code,200)
        mock.assert_called_once()
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"sandbox","ESTOA_WEBHOOK_PREVIEW":"true"})
    @patch("accounts_webhook_routes.receive_notification",side_effect=PermissionError)
    def test_invalid_signature(self,mock):
        self.assertEqual(self.client.post("/payments/webhook?data.id=abc").status_code,401)
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"sandbox","ESTOA_WEBHOOK_PREVIEW":"true"})
    def test_ambiguous_resource(self):
        self.assertEqual(self.client.post("/payments/webhook?data.id=a&data.id=b").status_code,400)
