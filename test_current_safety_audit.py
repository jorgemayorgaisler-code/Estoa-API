"""Synthetic regression checks; not a validation against SHOA tables."""
import unittest
from unittest.mock import patch
from datetime import datetime
import pandas as pd
import app

class CurrentSafetyTests(unittest.TestCase):
    def sample(self, maximum=6, reverse=False):
        a,b=("MAX_EBB","SLACK") if reverse else ("SLACK","MAX_FLOOD")
        return pd.DataFrame([
            dict(station_id="TEST",local_dt=pd.Timestamp("2026-11-26 23:00"),event_type=a,intensity_kn=maximum if reverse else 0,direction_true=90),
            dict(station_id="TEST",local_dt=pd.Timestamp("2026-11-27 02:00"),event_type=b,intensity_kn=0 if reverse else maximum,direction_true=90)])
    def query(self, frame, time):
        with patch.object(app,"EVENTS",frame), patch.object(app,"station_row"):
            return app.instant("TEST",datetime.fromisoformat(time))
    def test_midnight_rising(self):
        r=self.query(self.sample(),"2026-11-27T00:00")
        self.assertAlmostEqual(r["intensity_kn"],3)
        self.assertEqual(r["phase"],"FLOOD")
    def test_midnight_falling(self):
        r=self.query(self.sample(reverse=True),"2026-11-27T01:00")
        self.assertAlmostEqual(r["intensity_kn"],3)
        self.assertEqual(r["phase"],"EBB")
    def test_invalid_maxima(self):
        for v in (None,float("nan"),float("inf"),-1):
            with self.subTest(v=v):
                r=self.query(self.sample(v),"2026-11-27T00:00")
                self.assertIsNone(r["intensity_kn"])
                self.assertEqual(r["status"],"INVALID_SOURCE_VALUE")
    def test_outside_coverage(self):
        self.assertIsNone(self.query(self.sample(),"2026-11-27T03:00")["intensity_kn"])
    def test_weak_variable_gap(self):
        frame=self.sample()
        frame.loc[1,"event_type"]="WEAK_VARIABLE"
        self.assertIsNone(self.query(frame,"2026-11-27T00:00")["intensity_kn"])

if __name__=="__main__":
    unittest.main()
