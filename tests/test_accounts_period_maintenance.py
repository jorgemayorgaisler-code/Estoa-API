import os
import unittest
import uuid
from datetime import datetime,timedelta,timezone
from accounts_store import connection
from accounts_verified_periods import record_verified_period
from accounts_period_maintenance import reconcile_due_periods

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class PeriodMaintenanceTests(unittest.TestCase):
    def test_future_activation_and_expiry(self):
        aid=uuid.uuid4()
        pid=str(uuid.uuid4())
        payment=str(uuid.uuid4())
        start=datetime.now(timezone.utc)+timedelta(days=1)
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'authorized',990)",(pid,aid))
        try:
            self.assertIsNone(record_verified_period(pid,payment,990,start,start+timedelta(days=30)))
            reconcile_due_periods()
            with connection() as conn:
                self.assertIsNone(conn.execute("SELECT access_until FROM subscriptions WHERE provider_id=%s",(pid,)).fetchone()["access_until"])
                conn.execute("UPDATE subscription_payments SET period_start=now()-interval '1 day',period_end=now()+interval '29 days' WHERE provider_payment_id=%s",(payment,))
            reconcile_due_periods()
            with connection() as conn:
                self.assertIsNotNone(conn.execute("SELECT access_until FROM subscriptions WHERE provider_id=%s",(pid,)).fetchone()["access_until"])
                conn.execute("UPDATE subscription_payments SET period_start=now()-interval '31 days',period_end=now()-interval '1 day' WHERE provider_payment_id=%s",(payment,))
            reconcile_due_periods()
            with connection() as conn:
                self.assertIsNone(conn.execute("SELECT access_until FROM subscriptions WHERE provider_id=%s",(pid,)).fetchone()["access_until"])
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM subscription_payments WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM subscriptions WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
