import os
import unittest
import uuid
from accounts_store import connection
from accounts_webhook_worker import claim,finish

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class WorkerTests(unittest.TestCase):
    def test_recover_expired_lease(self):
        rid=str(uuid.uuid4())
        with connection() as conn:
            conn.execute("INSERT INTO payment_webhook_inbox(request_id,resource_id,received_at) VALUES (%s,'resource',now()-interval '1 day')",(rid,))
        try:
            first=claim()
            self.assertEqual(first["request_id"],rid)
            with connection() as conn:
                conn.execute("UPDATE payment_webhook_inbox SET lease_until=now()-interval '1 second' WHERE request_id=%s",(rid,))
            second=claim()
            self.assertEqual(second["request_id"],rid)
            self.assertEqual(second["attempts"],2)
            self.assertIsNone(finish(rid,first["lease_token"],True))
            self.assertEqual(finish(rid,second["lease_token"],True),"processed")
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM payment_webhook_inbox WHERE request_id=%s",(rid,))
