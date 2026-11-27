import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_email_routes import build_email_router

class EmailRoutesTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI()
        app.include_router(build_email_router())
        self.client=TestClient(app)
    @patch("accounts_email_routes.allow_attempt",return_value=False)
    def test_throttle(self,limit):
        self.assertEqual(self.client.post("/accounts/reset/request",json={"email":"a@example.com"}).status_code,429)
    @patch("accounts_email_routes.allow_attempt",return_value=True)
    @patch("accounts_email_routes.issue_reset",return_value=None)
    def test_unknown_email(self,issue,limit):
        self.assertEqual(self.client.post("/accounts/reset/request",json={"email":"a@example.com"}).json(),{"status":"accepted"})
    @patch("accounts_email_routes.allow_attempt",return_value=True)
    @patch("accounts_email_routes.consume_verification",return_value=False)
    def test_expired(self,consume,limit):
        self.assertEqual(self.client.post("/accounts/verification/confirm",json={"token":"a"*43}).status_code,400)
