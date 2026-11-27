import os
import unittest
import uuid
from accounts_store import connection
from accounts_maintenance import prune_auth_records,operational_counts

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class MaintenanceTests(unittest.TestCase):
    def test_expired_session_pruned(self):
        aid=uuid.uuid4()
        token=uuid.uuid4().bytes
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            conn.execute("INSERT INTO account_sessions(token_hash,account_id,created_at,expires_at) VALUES (%s,%s,now()-interval '10 days',now()-interval '8 days')",(token,aid))
        try:
            self.assertGreaterEqual(prune_auth_records()["sessions"],1)
            with connection() as conn:
                self.assertIsNone(conn.execute("SELECT 1 FROM account_sessions WHERE token_hash=%s",(token,)).fetchone())
            self.assertGreaterEqual(operational_counts()["verified_accounts"],1)
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
