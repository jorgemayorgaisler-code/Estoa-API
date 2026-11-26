import unittest
from fastapi.testclient import TestClient
from accounts_preview import app
from accounts_navigation import ROUTES

class PreviewTests(unittest.TestCase):
    def test_isolation(self):
        client=TestClient(app)
        for path in (*ROUTES,"/conditions/map"):
            self.assertEqual(client.get(path).status_code,404)
        self.assertEqual(client.get("/private/conditions/now",params={"station_id":"CUR011"}).status_code,401)
        self.assertEqual(client.get("/private/conditions/map").status_code,401)
        self.assertEqual(client.get("/health").status_code,200)
