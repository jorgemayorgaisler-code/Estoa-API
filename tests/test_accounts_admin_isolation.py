import unittest
from fastapi.testclient import TestClient
from accounts_preview import app

class AdminIsolationTests(unittest.TestCase):
    def test_admin_summary_not_mounted(self):
        client=TestClient(app)
        for headers in ({},{"Authorization":"Bearer "+"a"*43}):
            self.assertEqual(client.get("/admin/summary",headers=headers).status_code,404)
        self.assertNotIn("/admin/summary",app.openapi()["paths"])
