import os
import unittest
import uuid
from accounts_store import register, login, connection, session_account
from accounts_verification import issue_verification, consume_verification
from accounts_entitlements import activate_trial, allowed_stations, select_free_station
from accounts_reset import issue_reset, consume_reset
from accounts_rate_limits import allow_attempt

@unittest.skipUnless(os.getenv("ESTOA_TEST_DATABASE")=="1", "Requires isolated test database")
class AccountIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.email=f"{uuid.uuid4()}@example.test"
        self.password="test-password-long"
        self.aid=register(self.email,self.password)
        self.stations={"CUR001","CUR002"}
        self.addCleanup(self.cleanup_account)

    def cleanup_account(self):
        with connection() as conn:
            conn.execute("DELETE FROM accounts WHERE id=%s",(self.aid,))

    def verify(self):
        token=issue_verification(self.aid)
        self.assertTrue(consume_verification(token))
        self.assertFalse(consume_verification(token))

    def test_registration(self):
        self.assertIsNone(register(self.email,self.password))
        self.assertIsNone(login(self.email,self.password))
        self.verify()
        self.assertEqual(session_account(login(self.email,self.password)[0]),self.aid)

    def test_trial(self):
        self.verify()
        select_free_station(self.aid,"CUR001",self.stations)
        with self.assertRaises(PermissionError):
            select_free_station(self.aid,"CUR002",self.stations)
        first=activate_trial(self.aid)
        self.assertEqual(first["expires_at"],activate_trial(self.aid)["expires_at"])
        self.assertEqual(allowed_stations(self.aid,self.stations),self.stations)
        with connection() as conn:
            conn.execute("UPDATE premium_trials SET activated_at=now()-interval '2 months',expires_at=now()-interval '1 month' WHERE account_id=%s",(self.aid,))
        self.assertFalse(activate_trial(self.aid)["active"])
        self.assertEqual(allowed_stations(self.aid,self.stations),{"CUR001"})

    def test_reset(self):
        self.verify()
        session=login(self.email,self.password)[0]
        token=issue_reset(self.email)
        self.assertTrue(consume_reset(token,"new-password-long"))
        self.assertFalse(consume_reset(token,"other-password-long"))
        self.assertIsNone(session_account(session))
        self.assertIsNone(login(self.email,self.password))
        self.assertIsNotNone(login(self.email,"new-password-long"))

    def test_throttle(self):
        for _ in range(8):
            self.assertTrue(allow_attempt("login_email",self.email))
        self.assertFalse(allow_attempt("login_email",self.email))
