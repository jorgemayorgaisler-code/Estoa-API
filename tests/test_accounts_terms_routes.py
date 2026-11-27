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

    def test_document_and_acceptance_contract(self):
        app=FastAPI()
        app.include_router(build_router([]))
        client=TestClient(app)
        headers={"Authorization":"Bearer test"}
        metadata={"version":"test","content_sha256":"a"*64,"accepted_at":None}
        with patch("accounts_routes.store.session_account",return_value="account"), patch.dict("os.environ",{"ESTOA_TERMS_PREVIEW":"true"}), patch("accounts_terms.terms_status",return_value=metadata), patch("accounts_terms_content.verified_content",return_value="Texto de prueba"), patch("accounts_terms.accept_terms",return_value="2026-11-27T12:00:00Z") as accept:
            self.assertEqual(client.get("/accounts/me/terms",headers=headers).json(),dict(metadata,content="Texto de prueba"))
            result=client.post("/accounts/me/terms",headers=headers,json={"version":"test","consent":True})
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.json()["version"],"test")
            accept.assert_called_once_with("account","test",True)
        with patch("accounts_routes.store.session_account",return_value="account"), patch.dict("os.environ",{"ESTOA_TERMS_PREVIEW":"true"}), patch("accounts_terms.terms_status",return_value=metadata), patch("accounts_terms_content.verified_content",side_effect=ValueError), patch("accounts_terms.accept_terms") as accept:
            self.assertEqual(client.get("/accounts/me/terms",headers=headers).status_code,503)
            self.assertEqual(client.post("/accounts/me/terms",headers=headers,json={"version":"test","consent":True}).status_code,409)
            accept.assert_not_called()
