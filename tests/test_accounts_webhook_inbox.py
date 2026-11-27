import os
import unittest
import uuid
from unittest.mock import patch
from accounts_store import connection
from accounts_webhook_inbox import receive_notification

class SignatureTests(unittest.TestCase):
    @patch("accounts_webhook_inbox.verify_signature",return_value=False)
    def test_invalid_signature(self,mock):
        with self.assertRaises(PermissionError):
            receive_notification("resource","request","invalid")

@unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
class InboxTests(unittest.TestCase):
    @patch("accounts_webhook_inbox.verify_signature",return_value=True)
    def test_duplicate(self,mock):
        rid=str(uuid.uuid4())
        try:
            self.assertEqual(receive_notification("resource",rid,"signature"),"accepted")
            self.assertEqual(receive_notification("resource",rid,"signature"),"duplicate")
            with self.assertRaises(ValueError):
                receive_notification("different",rid,"signature")
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM payment_webhook_inbox WHERE request_id=%s",(rid,))
