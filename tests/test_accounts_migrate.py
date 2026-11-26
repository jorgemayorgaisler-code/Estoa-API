import os
import unittest
from unittest.mock import patch
from accounts_migrate import migrate
from accounts_store import connection

class MigrationTests(unittest.TestCase):
    @patch.dict(os.environ,{"ESTOA_MIGRATION_PREVIEW":"false"})
    def test_disabled(self):
        with self.assertRaises(RuntimeError):
            migrate()

    @unittest.skipUnless(os.environ.get("ESTOA_TEST_DATABASE")=="1","requires test database")
    @patch.dict(os.environ,{"ESTOA_MIGRATION_PREVIEW":"true"})
    def test_replay(self):
        count=migrate()
        self.assertGreaterEqual(count,12)
        self.assertEqual(migrate(),count)
        with connection() as conn:
            self.assertEqual(conn.execute("SELECT count(*) AS n FROM estoa_schema_history").fetchone()["n"],count)
