import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_routes import build_router

class DeletionRouteTests(unittest.TestCase):
    def test_authentication_and_password_type(self):
        app=FastAPI()
        app.include_router(build_router([]))
        client=TestClient(app)
        self.assertEqual(client.post("/accounts/me/deletion-request",json={"password":"long-password"}).status_code,401)
        with patch("accounts_routes.store.session_account",return_value="account"):
            headers={"Authorization":"Bearer token"}
            with patch.dict("os.environ",{"ESTOA_DELETION_PREVIEW":"true"}):
                self.assertEqual(client.post("/accounts/me/deletion-request",json={"password":123456789012},headers=headers).status_code,422)

    def test_status_and_submission_contract(self):
        app=FastAPI()
        app.include_router(build_router([]))
        client=TestClient(app)
        headers={"Authorization":"Bearer test"}
        result={"request_id":"test","status":"pending_review"}
        with patch("accounts_routes.store.session_account",return_value="account"), patch.dict("os.environ",{"ESTOA_DELETION_PREVIEW":"true"}), patch("accounts_routes.allow_attempt",return_value=True), patch("accounts_deletion.deletion_status",return_value=None), patch("accounts_deletion.request_deletion",return_value=result) as submit:
            self.assertEqual(client.get("/accounts/me/deletion-request",headers=headers).json(),{"request":None})
            response=client.post("/accounts/me/deletion-request",headers=headers,json={"password":"long-password"})
            self.assertEqual(response.status_code,202)
            self.assertEqual(response.json(),result)
            submit.assert_called_once_with("account","long-password")
