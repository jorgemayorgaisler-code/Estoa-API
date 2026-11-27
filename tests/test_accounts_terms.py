import os
import unittest
import uuid
from unittest.mock import patch
from accounts_terms import accept_terms, terms_status
from accounts_store import connection

class TermsTests(unittest.TestCase):
    @patch.dict(os.environ,{"ESTOA_TERMS_VERSION":"test-current"})
    def test_invalid_consent(self):
        for version,consent in (("old",True),("test-current",False),("test-current","true")):
            with self.assertRaises(ValueError):
                accept_terms(uuid.uuid4(),version,consent)

    @unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
    def test_acceptance_replay(self):
        aid=uuid.uuid4()
        version=str(uuid.uuid4())
        with connection() as conn:
            conn.execute("INSERT INTO accounts(id,email,password_hash,email_verified_at) VALUES (%s,%s,'test',now())",(aid,str(aid)+"@example.test"))
            conn.execute("INSERT INTO contractual_documents(version,content_sha256,published_at) VALUES (%s,%s,now())",(version,"a"*64))
        try:
            with patch.dict(os.environ,{"ESTOA_TERMS_VERSION":version}):
                self.assertIsNone(terms_status(aid)['accepted_at'])
                first=accept_terms(aid,version,True)
                self.assertEqual(terms_status(aid)['accepted_at'],first)
                self.assertEqual(terms_status(aid)['content_sha256'],'a'*64)
                self.assertEqual(first,accept_terms(aid,version,True))
                with self.assertRaises(PermissionError):
                    accept_terms(uuid.uuid4(),version,True)
        finally:
            with connection() as conn:
                conn.execute("DELETE FROM accounts WHERE id=%s",(aid,))
                conn.execute("DELETE FROM contractual_documents WHERE version=%s",(version,))
