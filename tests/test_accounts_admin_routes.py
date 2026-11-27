import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_admin_routes import build_admin_router
class AdminTests(unittest.TestCase):
    def test_permissions(self):
        app=FastAPI()
        app.include_router(build_admin_router())
        client=TestClient(app)
        self.assertEqual(client.get("/admin/summary").status_code,401)
        headers={"Authorization":"Bearer token"}
        with patch("accounts_admin_routes.session_account",return_value="account"):
            with patch("accounts_admin_routes.admin_summary",side_effect=PermissionError):
                self.assertEqual(client.get("/admin/summary",headers=headers).status_code,403)
            with patch("accounts_admin_routes.admin_summary",return_value={"verified_accounts":1}):
                self.assertEqual(client.get("/admin/summary",headers=headers).json(),{"verified_accounts":1})
