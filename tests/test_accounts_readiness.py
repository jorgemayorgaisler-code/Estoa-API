import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from accounts_preview import app
from accounts_readiness import database_ready

class ReadinessTests(unittest.TestCase):
    @patch("accounts_readiness.connection",side_effect=RuntimeError("secret database detail"))
    def test_unavailable(self,connection):
        self.assertFalse(database_ready())
        response=TestClient(app).get("/ready")
        self.assertEqual(response.status_code,503)
        self.assertNotIn("secret database detail",response.text)
        self.assertEqual(response.headers["cache-control"],"no-store")

    @patch("accounts_readiness.database_ready",return_value=True)
    def test_ready(self,ready):
        response=TestClient(app).get("/ready")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),{"status":"ready"})
        self.assertEqual(response.headers["cache-control"],"no-store")
