import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class RouteTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI()
        app.include_router(build_router({"CUR001","CUR002"}))
        self.client=TestClient(app)

    def test_private_routes(self):
        for method,path in [("GET","stations"),("POST","trial")]:
            self.assertEqual(self.client.request(method,"/accounts/me/"+path).status_code,401)

    @patch("accounts_routes.allow_attempt",return_value=False)
    def test_throttled_login(self, _):
        response=self.client.post("/accounts/login",json={"email":"test@example.test","password":"long-password"})
        self.assertEqual(response.status_code,429)
