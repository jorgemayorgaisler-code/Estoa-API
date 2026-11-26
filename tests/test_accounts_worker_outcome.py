import unittest
from accounts_webhook_worker import finish

class WorkerOutcomeTests(unittest.TestCase):
    def test_explicit_boolean_required(self):
        for value in ("false",1,None,{}):
            with self.assertRaises(ValueError):
                finish("test","test",value)
