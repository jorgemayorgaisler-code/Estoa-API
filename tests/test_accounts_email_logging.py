import unittest
from unittest.mock import patch
from accounts_email_routes import deliver

class EmailLoggingTests(unittest.TestCase):
    @patch("accounts_email_routes.send_code",side_effect=RuntimeError("private-secret"))
    def test_sanitized_failure(self,send):
        with self.assertLogs("estoa.email",level="WARNING") as logs:
            deliver("private@example.test","private-code","verify")
        self.assertIn("email_delivery_failed purpose=verify",logs.output[0])
        self.assertNotIn("private",logs.output[0])
