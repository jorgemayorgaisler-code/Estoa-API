"""Regression tests for PUB3015 empirical windows and station coverage."""
import unittest
import pandas as pd
from integrated_services import _nearest_minutes, weak_windows, METHODS, WEAK
from app import EVENTS

class WeakWindowTests(unittest.TestCase):
    def test_published_worked_examples(self):
        # PUB3015 2026 pp.166-168; (table, case, max_before, max_after, minutes_before, minutes_after)
        examples=[
            ("G","i",2.3,1.5,58,67),
            ("D","i",3.9,1.2,27,75),
            ("G","ii",2.5,2.6,150,150),
            ("C","ii",3.0,2.1,132,140),
            ("G","iii",2.5,2.4,109,110),
        ]
        for table,case,prev,nxt,before,after in examples:
            with self.subTest(table=table,case=case):
                self.assertEqual(_nearest_minutes(table,prev,1.0,case),before)
                self.assertEqual(_nearest_minutes(table,nxt,1.0,case),after)

    def test_empirical_windows_clipped_and_auditable(self):
        # Station and date from the official Kirke worked example, p.166.
        start=pd.Timestamp("2026-09-03T19:00:00")
        result=weak_windows("CUR011",start,1,1.0)
        self.assertTrue(result,"Kirke should have at least one empirical window in this period")
        for window in result:
            with self.subTest(window=window):
                self.assertGreaterEqual(pd.Timestamp(window["start"]),start)
                self.assertLessEqual(pd.Timestamp(window["end"]),start+pd.Timedelta(hours=1))
                self.assertLessEqual(pd.Timestamp(window["full_start"]),pd.Timestamp(window["start"]))
                self.assertGreaterEqual(pd.Timestamp(window["full_end"]),pd.Timestamp(window["end"]))
                self.assertEqual(window["method"],"PUB3015_EMPIRICAL_TABLE")

    def test_all_stations_thresholds_and_boundaries(self):
        self.assertTrue(len(METHODS)>=22)
        for sid in METHODS.station_id:
            data=EVENTS[EVENTS.station_id==sid]
            self.assertFalse(data.empty,sid)
            start=pd.Timestamp(data.local_dt.min())+pd.Timedelta(days=3)
            supported=[float(v) for v in str(METHODS.loc[METHODS.station_id==sid,"empirical_thresholds_kn"].iloc[0]).split(",")]
            for threshold in supported+[2.5]:
                with self.subTest(station=sid,threshold=threshold):
                    windows=weak_windows(sid,start,24,threshold)
                    for w in windows:
                        self.assertLess(pd.Timestamp(w["start"]),pd.Timestamp(w["end"]))
                        self.assertGreaterEqual(pd.Timestamp(w["start"]),start)
                        self.assertLessEqual(pd.Timestamp(w["end"]),start+pd.Timedelta(hours=24))
                        self.assertEqual(float(w["threshold_kn"]),threshold)

    def test_digitized_table_integrity(self):
        self.assertEqual(len(WEAK),1374)
        self.assertEqual(WEAK.duplicated(["table","max_intensity_kn","threshold_kn","case"]).sum(),0)

if __name__=="__main__":
    unittest.main()
