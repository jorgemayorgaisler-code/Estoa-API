import os
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime,timedelta,timezone
from accounts_store import connection
from accounts_verified_periods import record_verified_period,revoke_verified_payment

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class PaymentConcurrencyTests(unittest.TestCase):
    def test_conflicting_subscription_identity(self):
        aid=uuid.uuid4()
        p1,p2,payment=[str(uuid.uuid4()) for _ in range(3)]
        start=datetime.now(timezone.utc)-timedelta(days=1)
        barrier=Barrier(2)
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            for pid in (p1,p2):
                conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'authorized',990)",(pid,aid))
        def run(action):
            barrier.wait(timeout=10)
            try:
                action()
                return True
            except ValueError:
                return False
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                a=pool.submit(run,lambda:record_verified_period(p1,payment,990,start,start+timedelta(days=30)))
                b=pool.submit(run,lambda:revoke_verified_payment(p2,payment,"refunded"))
                self.assertEqual(sum([a.result(timeout=20),b.result(timeout=20)]),1)
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM payment_revocations WHERE provider_id IN (%s,%s)",(p1,p2))
                conn.execute("DELETE FROM subscription_payments WHERE provider_id IN (%s,%s)",(p1,p2))
                conn.execute("DELETE FROM subscriptions WHERE provider_id IN (%s,%s)",(p1,p2))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
