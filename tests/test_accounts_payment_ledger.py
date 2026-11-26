import os
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from accounts_store import connection
from accounts_payment_ledger import refresh_paid_access

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class LedgerTests(unittest.TestCase):
    def test_approved_period_and_refund(self):
        aid=uuid.uuid4()
        pid=str(uuid.uuid4())
        payment=str(uuid.uuid4())
        now=datetime.now(timezone.utc)
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,%s,now())",(aid,str(aid)+"@example.test","test"))
            conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'authorized',990)",(pid,aid))
        try:
            self.assertIsNone(refresh_paid_access(pid))
            with connection() as conn:
                conn.execute("INSERT INTO subscription_payments(provider_payment_id,provider_id,amount_clp,currency,period_start,period_end,status) VALUES (%s,%s,990,'CLP',%s,%s,'approved')",(payment,pid,now-timedelta(days=1),now+timedelta(days=29)))
            self.assertIsNotNone(refresh_paid_access(pid))
            with connection() as conn:
                conn.execute("UPDATE subscription_payments SET status='refunded' WHERE provider_payment_id=%s",(payment,))
            self.assertIsNone(refresh_paid_access(pid))
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM subscription_payments WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM subscriptions WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
