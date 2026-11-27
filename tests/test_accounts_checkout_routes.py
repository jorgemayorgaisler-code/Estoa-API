import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class CheckoutRouteTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI()
        app.include_router(build_router({"CUR001"}))
        self.client=TestClient(app)
        self.headers={"Authorization":"Bearer test"}

    def test_unauthenticated(self):
        self.assertEqual(self.client.post("/accounts/me/checkout",json={"consent":True}).status_code,401)

    @patch("accounts_routes.store.session_account",return_value="test-account")
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"production","ESTOA_CHECKOUT_PREVIEW":"true"})
    def test_production_blocked(self,_):
        self.assertEqual(self.client.post("/accounts/me/checkout",json={"consent":True},headers=self.headers).status_code,503)

    @patch("accounts_routes.store.session_account",return_value="test-account")
    @patch.dict("os.environ",{"ESTOA_MP_MODE":"sandbox","ESTOA_CHECKOUT_PREVIEW":"true"})
    def test_no_consent(self,_):
        self.assertEqual(self.client.post("/accounts/me/checkout",json={"consent":False},headers=self.headers).status_code,409)
