import os
import unittest
import uuid
from accounts_store import connection,register,login,session_account,revoke_all_sessions

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class GlobalLogoutTests(unittest.TestCase):
    def test_revoke_all(self):
        password="test-password-123"
        emails=[str(uuid.uuid4())+"@example.test" for _ in range(2)]
        ids=[register(email,password) for email in emails]
        try:
            with connection() as conn:
                for aid in ids:
                    conn.execute("UPDATE accounts SET email_verified_at=now() WHERE id=%s",(aid,))
            tokens=[login(emails[0],password)[0] for _ in range(2)]
            other=login(emails[1],password)[0]
            with self.assertRaises(PermissionError):
                revoke_all_sessions(ids[0],"wrong-password-123")
            self.assertEqual(session_account(tokens[0]),ids[0])
            self.assertEqual(revoke_all_sessions(ids[0],password),2)
            for token in tokens:
                self.assertIsNone(session_account(token))
            self.assertEqual(session_account(other),ids[1])
            self.assertEqual(revoke_all_sessions(ids[0],password),0)
        finally:
            with connection() as conn:
                for aid in ids:
                    conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
