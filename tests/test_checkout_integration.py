import os
import uuid
import unittest
from accounts_store import register, connection
from accounts_checkout import reserve_checkout

@unittest.skipUnless(os.getenv("ESTOA_TEST_DATABASE")=="1","Requires isolated database")
class CheckoutTests(unittest.TestCase):
    def test_duplicate(self):
        aid=register(f"{uuid.uuid4()}@example.test","test-password-long")
        try:
            with connection() as conn:
                conn.execute("UPDATE accounts SET email_verified_at=now() WHERE id=%s",(aid,))
            reserve_checkout(aid)
            with self.assertRaises(PermissionError):
                reserve_checkout(aid)
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM checkout_reservations WHERE account_id=%s",(aid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
