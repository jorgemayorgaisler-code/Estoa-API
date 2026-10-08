"""Representative end-to-end user journey against ESTOA's 2026 calculation engine."""
import unittest
from datetime import datetime
from app import stations, conditions_at, forecast, weak_windows_endpoint, tide_curve, tide_events, conditions_map


class UserJourney(unittest.TestCase):
    def test_kirke_select_date_consult_and_windows(self):
        catalog = stations()
        station = next(s for s in catalog if s["station_id"] == "CUR011")
        self.assertEqual(station["timezone_id"], "America/Punta_Arenas")
        moment = datetime(2026, 10, 4, 18, 30)
        condition = conditions_at(station["station_id"], moment)
        self.assertEqual(condition["station"]["station_id"], "CUR011")
        self.assertIn(condition["current"]["phase"], ("FLOOD", "EBB", "SLACK", "VARIABLE", "UNKNOWN"))
        self.assertGreaterEqual(condition["current"]["intensity_kn"], 0)
        events = forecast("CUR011", datetime(2026, 10, 4, 0), 24)
        self.assertEqual(events["station_id"], "CUR011")
        self.assertTrue(events["events"])
        windows = weak_windows_endpoint("CUR011", datetime(2026, 10, 4, 0), 24, 1.0)
        self.assertIsInstance(windows["windows"], list)
        self.assertEqual(windows["threshold_kn"], 1.0)
        curve = tide_curve("CUR011", datetime(2026, 10, 4, 12), 12)
        self.assertEqual(len(curve["samples"]), 25)
        self.assertTrue(all("height_m" in sample for sample in curve["samples"]))
        tide = tide_events("CUR011", "2026-10-04T00:00:00", 24)
        self.assertIsInstance(tide["events"], list)

    def test_map_uses_civil_station_time(self):
        mapped = conditions_map(datetime.fromisoformat("2026-07-15T15:00:00+00:00"))
        self.assertEqual(len(mapped["stations"]), 22)
        by_id = {s["station_id"]: s for s in mapped["stations"]}
        self.assertEqual(by_id["CUR001"]["local_datetime"], "2026-07-15T11:00:00")
        self.assertEqual(by_id["CUR005"]["local_datetime"], "2026-07-15T12:00:00")
        self.assertEqual(by_id["CUR011"]["local_datetime"], "2026-07-15T12:00:00")


if __name__ == "__main__":
    unittest.main()
