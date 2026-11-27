import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class DeletionRouteTests(unittest.TestCase):
    def test_authentication_and_password_type(self):
        app=FastAPI()
        app.include_router(build_router([]))
        client=TestClient(app)
        self.assertEqual(client.post("/accounts/me/deletion-request",json={"password":"long-password"}).status_code,401)
        with patch("accounts_routes.store.session_account",return_value="account"):
            headers={"Authorization":"Bearer token"}
            with patch.dict("os.environ",{"ESTOA_DELETION_PREVIEW":"true"}):
                self.assertEqual(client.post("/accounts/me/deletion-request",json={"password":123456789012},headers=headers).status_code,422)
