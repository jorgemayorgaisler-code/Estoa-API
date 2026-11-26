import hashlib
import hmac
import unittest
from unittest.mock import patch
from accounts_webhooks import verify_signature

class WebhookTests(unittest.TestCase):
    @patch.dict("os.environ",{"ESTOA_MP_WEBHOOK_SECRET":"test-only-secret"})
    def test_signature(self):
        ts="1800000000"
        digest=hmac.new(b"test-only-secret",f"id:abc;request-id:req-1;ts:{ts};".encode(),hashlib.sha256).hexdigest()
        sig=f"ts={ts},v1={digest}"
        self.assertTrue(verify_signature("ABC","req-1",sig,now=int(ts)))
        self.assertFalse(verify_signature("other","req-1",sig,now=int(ts)))
        self.assertFalse(verify_signature("ABC","req-2",sig,now=int(ts)))
        self.assertFalse(verify_signature("ABC","req-1",sig,now=int(ts)+301))
        self.assertFalse(verify_signature("ABC","req-1",sig+",ts="+ts,now=int(ts)))
        self.assertFalse(verify_signature("ABC","req-1","",now=int(ts)))
