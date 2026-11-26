import unittest
from unittest.mock import patch
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from accounts_station_guard import build_station_guard

class GuardTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI()
        @app.get("/private/{station_id}")
        def route(station_id: str, account=Depends(build_station_guard({"CUR001","CUR002"}))):
            return {"station":station_id}
        self.client=TestClient(app)
        self.headers={"Authorization":"Bearer test"}

    def test_missing_session(self):
        self.assertEqual(self.client.get("/private/CUR001").status_code,401)

    @patch("accounts_station_guard.session_account",return_value="account")
    @patch("accounts_station_guard.require_station",side_effect=PermissionError)
    def test_denied(self,check,session):
        self.assertEqual(self.client.get("/private/CUR002",headers=self.headers).status_code,403)

    @patch("accounts_station_guard.session_account",return_value="account")
    @patch("accounts_station_guard.require_station")
    def test_allowed(self,check,session):
        self.assertEqual(self.client.get("/private/CUR001",headers=self.headers).status_code,200)
        check.assert_called_once()
