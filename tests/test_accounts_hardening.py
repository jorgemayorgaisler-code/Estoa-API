import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class HardeningTests(unittest.TestCase):
    def test_string_consent_rejected(self):
        app=FastAPI()
        app.include_router(build_router({"CUR001"}))
        with patch("accounts_store.session_account",return_value="account"):
            response=TestClient(app).post("/accounts/me/checkout",json={"consent":"true"},headers={"Authorization":"Bearer token"})
        self.assertEqual(response.status_code,422)

    def test_preview_headers(self):
        from accounts_preview import app
        response=TestClient(app).get("/private/stations")
        self.assertEqual(response.headers["Cache-Control"],"no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"],"nosniff")
        self.assertEqual(response.headers["Referrer-Policy"],"no-referrer")
