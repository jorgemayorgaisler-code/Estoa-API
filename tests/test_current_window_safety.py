"""Additional safety regression checks for ESTOA current-window provenance."""
import unittest
from unittest.mock import patch
import pandas as pd
from integrated_services import _nearest_minutes, weak_windows, weak_windows_diagnostics, WEAK
from app import EVENTS, current_curve


class CurrentWindowSafetyTests(unittest.TestCase):
    def test_current_curve_chart_contract(self):
        start = pd.Timestamp("2026-10-07T00:00:00")
        result = current_curve("CUR011", start.to_pydatetime(), 1, 30)
        self.assertEqual(len(result["samples"]), 3)
        self.assertEqual(result["samples"][0]["time_local"], start.isoformat())
        self.assertEqual(result["samples"][-1]["time_local"], "2026-10-07T01:00:00")
        self.assertTrue(all("method" in s and "intensity_kn" in s for s in result["samples"]))

    def test_current_curve_preserves_missing_data(self):
        with patch("app.instant", return_value={
            "status": "OUT_OF_DATASET", "intensity_kn": None,
            "phase": "UNKNOWN", "trend": "UNKNOWN", "direction_true": None
        }):
            result = current_curve("CUR011", pd.Timestamp("2026-10-07").to_pydatetime(), 1, 60)
        self.assertTrue(all(s["intensity_kn"] is None for s in result["samples"]))

    def test_midpoint_ties_are_not_silently_guessed(self):
        # Synthetic fixture avoids floating-point midpoint ambiguity in source CSV.
        table = pd.DataFrame([
            {"table": "T", "threshold_kn": 1.0, "case": "i",
             "max_intensity_kn": 2.0, "minutes": 60},
            {"table": "T", "threshold_kn": 1.0, "case": "i",
             "max_intensity_kn": 4.0, "minutes": 30},
        ])
        with patch("integrated_services.WEAK", table):
            self.assertIsNone(_nearest_minutes("T", 3.0, 1.0, "i"))
            self.assertEqual(_nearest_minutes("T", 2.0, 1.0, "i"), 60)

    def test_diagnostics_reject_nonfinite_threshold(self):
        with self.assertRaises(ValueError):
            weak_windows_diagnostics("CUR011", pd.Timestamp("2026-10-07"), 24, float("nan"))

    def test_empty_results_keep_selected_method_provenance(self):
        # Empty windows must not silently reclassify empirical SHOA lookups.
        with patch("integrated_services.weak_windows", return_value=[]):
            empirical = weak_windows_diagnostics(
                "CUR011", pd.Timestamp("2026-10-07"), 24, 1.0)
            self.assertEqual(empirical["method"], "PUB3015_EMPIRICAL_TABLE")
            self.assertFalse(empirical["has_windows"])
            self.assertTrue(empirical["empty_result_note"])

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
