import unittest
from fastapi.testclient import TestClient
from accounts_preview import app
class CacheTests(unittest.TestCase):
    def test_private_denial_no_store(self):
        r=TestClient(app).get("/private/stations")
        self.assertEqual(r.status_code,401)
        self.assertEqual(r.headers["cache-control"],"no-store")
