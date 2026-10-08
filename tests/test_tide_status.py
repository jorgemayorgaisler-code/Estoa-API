"""Regression checks for the ESTOA tide panel and its source distinctions."""
import unittest
from datetime import datetime
from app import conditions_at
from tide_engine import tide_at


class TideStatusTests(unittest.TestCase):
    def test_kirke_condition_payload_has_tide(self):
        response = conditions_at("CUR011", datetime(2026, 10, 7, 18, 30))
        self.assertIn("tide", response)
        self.assertIn("capability", response["tide"])

    def test_available_tide_has_explicit_method_and_trend(self):
        result = tide_at("CUR011", datetime(2026, 10, 7, 18, 30))
        if result.get("available"):
            self.assertIn(result.get("trend"), ("RISING", "FALLING", "EVENT"))
            self.assertIn(result.get("method"), (
                "PUB3009_PUBLISHED_EVENT",
                "PUB3009_EVENT_TIMES_ONLY",
                "PUB3009_DIRECT_COSINE",
            ))
            if result.get("method") == "PUB3009_EVENT_TIMES_ONLY":
                self.assertIsNone(result.get("height_m"))

    def test_out_of_dataset_never_invents_height(self):
        result = tide_at("CUR011", datetime(2035, 1, 1))
        self.assertFalse(result.get("available"))
        self.assertIsNone(result.get("height_m"))


if __name__ == "__main__":
    unittest.main()
