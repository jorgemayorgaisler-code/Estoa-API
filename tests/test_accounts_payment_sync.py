import os
import unittest
import uuid
from unittest.mock import patch
from accounts_store import connection
from accounts_payment_sync import reconcile_subscription

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class PaymentSyncTests(unittest.TestCase):
    def test_reconciliation(self):
        aid=uuid.uuid4()
        pid,event=str(uuid.uuid4()),str(uuid.uuid4())
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'pending',990)",(pid,aid))
        data={"id":pid,"external_reference":str(aid),"status":"authorized","auto_recurring":{"currency_id":"CLP","transaction_amount":990,"frequency":1,"frequency_type":"months"}}
        try:
            with patch("accounts_payment_sync.fetch_subscription",return_value=dict(data,external_reference="wrong")):
                with self.assertRaises(ValueError):
                    reconcile_subscription(pid,event)
            with patch("accounts_payment_sync.fetch_subscription",return_value=data) as fetch:
                self.assertEqual(reconcile_subscription(pid,event),"authorized")
                self.assertEqual(reconcile_subscription(pid,event),"duplicate")
                self.assertEqual(fetch.call_count,1)
            with connection() as conn:
                row=conn.execute("SELECT status,access_until FROM subscriptions WHERE provider_id=%s",(pid,)).fetchone()
                self.assertEqual(row["status"],"authorized")
                self.assertIsNone(row["access_until"])
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM payment_webhook_events WHERE provider_event_id=%s",(event,))
                conn.execute("DELETE FROM subscriptions WHERE provider_id=%s",(pid,))
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
