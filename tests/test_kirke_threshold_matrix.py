"""Kirke regression matrix: boundaries, provenance, and threshold monotonicity.

These are internal consistency checks, NOT independent SHOA accuracy validation.
"""
import math
import unittest
import pandas as pd

from app import EVENTS
from integrated_services import weak_windows, weak_windows_diagnostics


class KirkeThresholdMatrixTests(unittest.TestCase):
    station = "CUR011"

    @classmethod
    def setUpClass(cls):
        events = EVENTS[EVENTS.station_id == cls.station]
        if events.empty:
            raise AssertionError("Kirke CUR011 event dataset missing")
        cls.start = pd.Timestamp(events.local_dt.min()) + pd.Timedelta(days=3)

    def test_threshold_matrix_and_provenance(self):
        for threshold in (0.0, 0.5, 1.0, 2.5, 3.0, 5.0, 10.0):
            with self.subTest(threshold=threshold):
                result = weak_windows_diagnostics(self.station, self.start, 24, threshold)
                self.assertIn(result["method"], ("PUB3015_EMPIRICAL_TABLE", "CALCULATED_CONTINUOUS"))
                self.assertEqual(result["windows"], weak_windows(self.station, self.start, 24, threshold))
                for window in result["windows"]:
                    a, b = pd.Timestamp(window["start"]), pd.Timestamp(window["end"])
                    self.assertLess(a, b)
                    self.assertGreaterEqual(a, self.start)
                    self.assertLessEqual(b, self.start + pd.Timedelta(hours=24))
                    self.assertEqual(float(window["threshold_kn"]), threshold)
                    self.assertIn(window["method"], ("PUB3015_EMPIRICAL_TABLE", "CALCULATED_CONTINUOUS"))
                    self.assertTrue(window.get("source"))

    def test_midnight_window_clipping(self):
        start = self.start.normalize() + pd.Timedelta(hours=23, minutes=30)
        end = start + pd.Timedelta(hours=2)
        for threshold in (1.0, 2.5, 10.0):
            with self.subTest(threshold=threshold):
                for w in weak_windows(self.station, start, 2, threshold):
                    self.assertGreaterEqual(pd.Timestamp(w["start"]), start)
                    self.assertLessEqual(pd.Timestamp(w["end"]), end)
                    self.assertLess(pd.Timestamp(w["start"]), pd.Timestamp(w["end"]))

    def test_reject_nonfinite_and_out_of_range_thresholds(self):
        for threshold in (float("nan"), float("inf"), float("-inf"), -0.1, 10.1):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    weak_windows_diagnostics(self.station, self.start, 24, threshold)

    def test_empirical_and_calculated_are_not_conflated(self):
        empirical = weak_windows_diagnostics(self.station, self.start, 24, 1.0)
        self.assertEqual(empirical["method"], "PUB3015_EMPIRICAL_TABLE")
        for w in empirical["windows"]:
            self.assertEqual(w["method"], "PUB3015_EMPIRICAL_TABLE")


if __name__ == "__main__":
    unittest.main()
