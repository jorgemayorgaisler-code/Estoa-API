import os
import unittest
import uuid
from accounts_store import connection
from accounts_admin import admin_summary

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class AdminIntegrationTests(unittest.TestCase):
    def test_grant_revoke_disable(self):
        aid=uuid.uuid4()
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
        try:
            with self.assertRaises(PermissionError):
                admin_summary(aid)
            with connection() as conn:
                conn.execute("INSERT INTO account_admin_grants(account_id) VALUES (%s)",(aid,))
            summary=admin_summary(aid)
            with connection() as conn:
                self.assertEqual(conn.execute("SELECT count(*) AS n FROM admin_access_audit WHERE account_id=%s",(aid,)).fetchone()["n"],1)
            self.assertEqual(set(summary),{"verified_accounts","active_trials","paid_accounts","approved_ledger_clp","review_notifications","pending_deletions","billing_deletions","expiring_paid_accounts","trial_paid_accounts"})
            with connection() as conn:
                conn.execute("UPDATE account_admin_grants SET revoked_at=now() WHERE account_id=%s",(aid,))
            with self.assertRaises(PermissionError):
                admin_summary(aid)
            with connection() as conn:
                conn.execute("UPDATE account_admin_grants SET revoked_at=NULL WHERE account_id=%s",(aid,))
                conn.execute("UPDATE accounts SET disabled_at=now() WHERE id=%s",(aid,))
            with self.assertRaises(PermissionError):
                admin_summary(aid)
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM admin_access_audit WHERE account_id=%s",(aid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
