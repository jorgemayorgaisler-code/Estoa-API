"""Additional safety regression checks for ESTOA current-window provenance."""
import unittest
import pandas as pd
from integrated_services import _nearest_minutes, weak_windows, weak_windows_diagnostics, WEAK
from app import EVENTS


class CurrentWindowSafetyTests(unittest.TestCase):
    def test_midpoint_ties_are_not_silently_guessed(self):
        # Choose a real pair of adjacent tabulated maximum intensities.
        for (_, threshold, case), group in WEAK.groupby(["table", "threshold_kn", "case"]):
            values = sorted(set(float(x) for x in group.max_intensity_kn))
            if len(values) < 2:
                continue
            table = str(group.iloc[0]["table"])
            midpoint = (values[0] + values[1]) / 2
            self.assertIsNone(_nearest_minutes(table, midpoint, threshold, case))
            return
        self.fail("No table has two adjacent maximum intensities")

    def test_diagnostics_reject_nonfinite_threshold(self):
        with self.assertRaises(ValueError):
            weak_windows_diagnostics("CUR011", pd.Timestamp("2026-10-07"), 24, float("nan"))

    def test_diagnostics_preserve_empirical_intervals(self):
        sid = "CUR011"
        g = EVENTS[EVENTS.station_id == sid]
        start = pd.Timestamp(g.local_dt.min()) + pd.Timedelta(days=3)
        result = weak_windows_diagnostics(sid, start, 24, 1.0)
        self.assertEqual(result["windows"], weak_windows(sid, start, 24, 1.0))
        self.assertEqual(result["overlap_count"], sum(bool(w.get("overlaps_previous")) for w in result["windows"]))
        self.assertIn("operational_notice", result)

    def test_method_provenance_and_query_bounds(self):
        sid = "CUR011"
        g = EVENTS[EVENTS.station_id == sid]
        self.assertFalse(g.empty)
        start = pd.Timestamp(g.local_dt.min()) + pd.Timedelta(days=3)
        end = start + pd.Timedelta(hours=24)
        for threshold in (0.5, 1.0, 2.5, 3.0, 10.0):
            with self.subTest(threshold=threshold):
                for window in weak_windows(sid, start, 24, threshold):
                    lo, hi = pd.Timestamp(window["start"]), pd.Timestamp(window["end"])
                    self.assertLess(lo, hi)
                    self.assertGreaterEqual(lo, start)
                    self.assertLessEqual(hi, end)
                    self.assertIn(window["method"], ("PUB3015_EMPIRICAL_TABLE", "CALCULATED_CONTINUOUS"))
                    self.assertTrue(window.get("source"))
                    if window["method"] == "PUB3015_EMPIRICAL_TABLE":
                        self.assertIn("table", window)
                        self.assertIn("full_start", window)
                        self.assertIn("full_end", window)


if __name__ == "__main__":
    unittest.main()
