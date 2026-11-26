import os
import unittest
import uuid
from datetime import datetime,timedelta,timezone
from accounts_store import connection
from accounts_verified_periods import record_verified_period,revoke_verified_payment

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class VerifiedPeriodTests(unittest.TestCase):
    def test_period_and_revocation(self):
        aid=uuid.uuid4()
        pid=str(uuid.uuid4())
        payment=str(uuid.uuid4())
        start=datetime.now(timezone.utc)-timedelta(days=1)
        end=start+timedelta(days=30)
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'authorized',990)",(pid,aid))
        try:
            self.assertEqual(record_verified_period(pid,payment,990,start,end),end)
            self.assertEqual(record_verified_period(pid,payment,990,start,end),end)
            with self.assertRaises(ValueError):
                record_verified_period(pid,str(uuid.uuid4()),990,start,end)
            with self.assertRaises(ValueError):
                record_verified_period(pid,payment,990,start,end+timedelta(days=1))
            with self.assertRaises(ValueError):
                record_verified_period(pid,str(uuid.uuid4()),990,start+timedelta(days=2),end+timedelta(days=2))
            self.assertIsNone(revoke_verified_payment(pid,payment,"refunded"))
            self.assertIsNone(record_verified_period(pid,payment,990,start,end))
            self.assertIsNone(revoke_verified_payment(pid,payment,"charged_back"))
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM subscription_payments WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM subscriptions WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
