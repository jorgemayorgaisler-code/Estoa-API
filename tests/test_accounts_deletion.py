import os
import unittest
import uuid
from accounts_store import connection, register
from accounts_deletion import request_deletion

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class DeletionTests(unittest.TestCase):
    def test_billing_review_and_replay(self):
        password="test-password-123"
        aid=register(str(uuid.uuid4())+"@example.test",password)
        pid=str(uuid.uuid4())
        try:
            with connection() as conn:
                conn.execute("UPDATE accounts SET email_verified_at=now() WHERE id=%s",(aid,))
                conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'authorized',990)",(pid,aid))
            with self.assertRaises(PermissionError):
                request_deletion(aid,"wrong-password-123")
            result=request_deletion(aid,password)
            self.assertEqual(result["status"],"billing_review")
            self.assertEqual(request_deletion(aid,password),result)
            with connection() as conn:
                self.assertIsNone(conn.execute("SELECT disabled_at FROM accounts WHERE id=%s",(aid,)).fetchone()["disabled_at"])
                self.assertEqual(conn.execute("SELECT status FROM subscriptions WHERE provider_id=%s",(pid,)).fetchone()["status"],"authorized")
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM subscriptions WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
