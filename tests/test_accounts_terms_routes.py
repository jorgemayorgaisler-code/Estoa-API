import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class TermsRouteTests(unittest.TestCase):
    def test_guards(self):
        app=FastAPI()
        app.include_router(build_router([]))
        client=TestClient(app)
        body={"version":"test","consent":True}
        self.assertEqual(client.post("/accounts/me/terms",json=body).status_code,401)
        with patch("accounts_routes.store.session_account",return_value="account"), patch.dict("os.environ",{"ESTOA_TERMS_PREVIEW":"false"}):
            headers={"Authorization":"Bearer test"}
            self.assertEqual(client.post("/accounts/me/terms",json=body,headers=headers).status_code,503)
            self.assertEqual(client.post("/accounts/me/terms",json=dict(body,consent="true"),headers=headers).status_code,422)
