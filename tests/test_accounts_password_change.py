import os
import unittest
import uuid
from accounts_store import connection,register,login,session_account,change_password
from accounts_reset import issue_reset,consume_reset

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class PasswordChangeTests(unittest.TestCase):
    def test_rotation(self):
        email=str(uuid.uuid4())+"@example.test"
        old="old-password-123"
        new="new-password-456"
        aid=register(email,old)
        try:
            with connection() as conn:
                conn.execute("UPDATE accounts SET email_verified_at=now() WHERE id=%s",(aid,))
            token=login(email,old)[0]
            reset=issue_reset(email)
            with self.assertRaises(PermissionError):
                change_password(aid,"wrong-password-123",new)
            self.assertEqual(session_account(token),aid)
            change_password(aid,old,new)
            self.assertIsNone(session_account(token))
            self.assertIsNone(login(email,old))
            self.assertFalse(consume_reset(reset,old))
            self.assertIsNotNone(login(email,new))
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
