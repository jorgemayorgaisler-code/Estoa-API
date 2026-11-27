import unittest
from unittest.mock import patch
from accounts_mail import send_code

class MailTests(unittest.TestCase):
    @patch.dict("os.environ",{"ESTOA_SMTP_HOST":"smtp.example.test","ESTOA_SMTP_FROM":"estoa@example.test","ESTOA_SMTP_USER":"test","ESTOA_SMTP_PASSWORD":"test-secret","ESTOA_SMTP_PORT":"465"})
    @patch("accounts_mail.smtplib.SMTP_SSL")
    def test_delivery(self,smtp):
        client=smtp.return_value.__enter__.return_value
        for purpose,subject in (("verify","ESTOA: verifica tu cuenta"),("reset","ESTOA: recupera tu contraseña")):
            send_code("user@example.test","test-code",purpose)
            msg=client.send_message.call_args.args[0]
            self.assertEqual(msg["Subject"],subject)
            self.assertEqual(msg["To"],"user@example.test")
            self.assertIn("test-code",msg.get_content())
            self.assertNotIn("test-secret",msg.get_content())
        self.assertEqual(smtp.call_args.args,("smtp.example.test",465))
        self.assertTrue(smtp.call_args.kwargs["context"].check_hostname)

    @patch("accounts_mail.smtplib.SMTP_SSL")
    def test_unknown_purpose(self,smtp):
        with self.assertRaises(ValueError):
            send_code("user@example.test","test-code","other")
        smtp.assert_not_called()
