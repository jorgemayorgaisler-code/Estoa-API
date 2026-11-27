import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from accounts_preview import app

class CatalogTests(unittest.TestCase):
    def test_requires_session(self):
        self.assertEqual(TestClient(app).get("/private/stations").status_code,401)
    @patch("accounts_preview.session_account",return_value="account")
    @patch("accounts_preview.allowed_stations",return_value={"CUR011"})
    def test_flags(self,allowed,session):
        r=TestClient(app).get("/private/stations",headers={"Authorization":"Bearer test"})
        self.assertEqual(r.status_code,200)
        self.assertEqual([s["station_id"] for s in r.json() if s["included"]],["CUR011"])
