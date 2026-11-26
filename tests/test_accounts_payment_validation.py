import unittest
from accounts_payment_validation import validate_payment
class PaymentEvidenceTests(unittest.TestCase):
    def test_evidence(self):
        p=dict(id=123,collector_id=456,currency_id="CLP",status="approved",transaction_amount=990,transaction_amount_refunded=0)
        self.assertTrue(validate_payment(p,123,990,456))
        for changes in [dict(status="pending"),dict(currency_id="USD"),dict(transaction_amount=2990),dict(transaction_amount_refunded=1),dict(collector_id=789),dict(transaction_amount_refunded=None)]:
            with self.assertRaises(ValueError):
                validate_payment(dict(p,**changes),123,990,456)
