import unittest
from datetime import datetime, timezone
from accounts_security import hash_password, verify_password, new_session, session_digest

class SecurityTests(unittest.TestCase):
    def test_password(self):
        password = "example-long-password"
        encoded = hash_password(password)
        self.assertTrue(encoded.startswith("$argon2id$"))
        self.assertTrue(verify_password(password, encoded))
        self.assertFalse(verify_password("incorrect-password", encoded))
        self.assertFalse(verify_password(password, "invalid"))
        self.assertNotEqual(encoded, hash_password(password))

    def test_password_length(self):
        for password in ("short", "x"*129):
            with self.assertRaises(ValueError):
                hash_password(password)

    def test_session(self):
        token, digest, expiry = new_session()
        self.assertEqual(len(token), 43)
        self.assertEqual(digest, session_digest(token))
        self.assertEqual(len(digest), 32)
        self.assertGreater(expiry, datetime.now(timezone.utc))
        self.assertNotEqual(token, new_session()[0])

if __name__ == "__main__":
    unittest.main()
