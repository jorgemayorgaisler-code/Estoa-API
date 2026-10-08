"""Functional API contract smoke tests for ESTOA 2026."""
import unittest
from datetime import datetime
from fastapi import HTTPException
from app import stations, conditions_at, capabilities, weak_windows_endpoint, version, health


class ApiContracts(unittest.TestCase):
    def test_health_and_version(self):
        self.assertEqual(health()["status"], "ok")
        self.assertEqual(version()["edition"], 2026)

    def test_station_catalog(self):
        catalog = stations()
        self.assertEqual(len(catalog), 22)
        ids = [s["station_id"] for s in catalog]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertIn("CUR011", ids)
        for sid in ("CUR005", "CUR006", "CUR007", "CUR008"):
            self.assertEqual(next(s for s in catalog if s["station_id"] == sid)["timezone_id"], "America/Coyhaique")

    def test_kirke_conditions_contract(self):
        result = conditions_at("CUR011", datetime(2026, 10, 4, 18, 30))
        self.assertEqual(result["station"]["station_id"], "CUR011")
        self.assertIn("current", result)
        self.assertIn("tide", result)
        self.assertEqual(result["astronomy"]["role"], "CONTEXT_ONLY")
        self.assertIsNotNone(result["current"].get("intensity_kn"))

    def test_station_capabilities(self):
        result = capabilities("CUR011")
        self.assertEqual(result["station_id"], "CUR011")
        self.assertIn("tide", result)

    def test_weak_window_parameter_validation(self):
        for hours, threshold in [(0, 1), (169, 1), (24, -0.1), (24, 10.1), (24, float("nan"))]:
            with self.subTest(hours=hours, threshold=threshold):
                with self.assertRaises(HTTPException) as caught:
                    weak_windows_endpoint("CUR011", datetime(2026, 10, 4, 0), hours, threshold)
                self.assertEqual(caught.exception.status_code, 422)

    def test_unknown_station_rejected(self):
        with self.assertRaises(HTTPException) as caught:
            conditions_at("UNKNOWN", datetime(2026, 10, 4, 18, 30))
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
