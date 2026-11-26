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
    def test_station_timezone(self):
        from types import SimpleNamespace
        with patch.object(app,"station_row",return_value=SimpleNamespace(timezone_id="America/Punta_Arenas")):
            for source, expected in [
                ("2026-11-26T12:00:00+00:00","2026-11-26T09:00:00"),
                ("2026-11-26T12:00:00-04:00","2026-11-26T13:00:00"),
                ("2026-11-26T01:00:00+00:00","2026-11-25T22:00:00"),
                ("2026-11-26T12:00:00","2026-11-26T12:00:00")]:
                self.assertEqual(app.station_local_datetime("TEST",datetime.fromisoformat(source)),datetime.fromisoformat(expected))
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
    def test_exact_invalid_maxima(self):
        for v in (None,float("nan"),float("inf"),-1):
            with self.subTest(v=v):
                r=self.query(self.sample(v),"2026-11-27T02:00")
                self.assertIsNone(r["intensity_kn"])
                self.assertEqual(r["status"],"INVALID_SOURCE_VALUE")
    def test_outside_coverage(self):
        self.assertIsNone(self.query(self.sample(),"2026-11-27T03:00")["intensity_kn"])
    def test_weak_variable_gap(self):
        frame=self.sample()
        frame.loc[1,"event_type"]="WEAK_VARIABLE"
        self.assertIsNone(self.query(frame,"2026-11-27T00:00")["intensity_kn"])

class TideSafetyTests(unittest.TestCase):
    def query(self, types, heights):
        import tide_engine
        frame=pd.DataFrame([
            dict(station_id="TEST",local_dt=pd.Timestamp("2026-11-26 00:00"),type=types[0],height_m=heights[0]),
            dict(station_id="TEST",local_dt=pd.Timestamp("2026-11-26 06:00"),type=types[1],height_m=heights[1])])
        with patch.object(tide_engine,"TIDES",frame):
            return tide_engine.tide_at("TEST",datetime(2026,11,26,3))
    def test_valid_tides(self):
        for types, heights in [(("LW","HW"),(0,4)),(("HW","LW"),(4,0))]:
            self.assertAlmostEqual(self.query(types,heights)["height_m"],2)
    def test_invalid_tides(self):
        for types, heights in [(("HW","HW"),(2,4)),(("LW","LW"),(1,2)),(("LW","HW"),(4,1)),(("HW","LW"),(1,4)),(("LW","HW"),(0,float("inf"))), (("LW","HW"),(None,4))]:
            with self.subTest(types=types,heights=heights):
                self.assertIsNone(self.query(types,heights)["height_m"])

class SolarSafetyTests(unittest.TestCase):
    def test_magallanes_solar_events(self):
        from types import SimpleNamespace
        from datetime import timedelta
        with patch.object(app,"station_row",return_value=SimpleNamespace(latitude=-51.73,longitude=-72.51,timezone_id="America/Punta_Arenas")):
            for day in ("2026-06-21","2026-12-21"):
                result=app.sun_events("TEST",day)
                self.assertEqual(result["status"],"CALCULATED_ASTRONOMICAL")
                rise=datetime.fromisoformat(result["sunrise"])
                setting=datetime.fromisoformat(result["sunset"])
                self.assertEqual(rise.utcoffset(),timedelta(hours=-3))
                self.assertEqual(rise.date().isoformat(),day)
                self.assertEqual(setting.date().isoformat(),day)
                self.assertLess(rise,setting)
    def test_missing_coordinates(self):
        from types import SimpleNamespace
        with patch.object(app,"station_row",return_value=SimpleNamespace(latitude=None,longitude=None)):
            self.assertEqual(app.sun_events("TEST","2026-11-26")["status"],"NO_COORDINATES")

class EndpointSafetyTests(unittest.TestCase):
    def test_invalid_horizons(self):
        from fastapi import HTTPException
        with patch.object(app,"station_row"):
            for endpoint,start in [(app.forecast,datetime(2026,11,26)),(app.tide_events,"2026-11-26T00:00")]:
                for hours in (-1,0,169,1000000):
                    with self.subTest(endpoint=endpoint.__name__,hours=hours):
                        with self.assertRaises(HTTPException) as caught:
                            endpoint("TEST",start,hours)
                        self.assertEqual(caught.exception.status_code,422)
    def test_invalid_tide_date(self):
        from fastapi import HTTPException
        with patch.object(app,"station_row"):
            with self.assertRaises(HTTPException) as caught:
                app.tide_events("TEST","not-a-date",24)
            self.assertEqual(caught.exception.status_code,422)
    def test_tide_events_timezone(self):
        from types import SimpleNamespace
        import tide_engine
        frame=pd.DataFrame([dict(station_id="TEST",local_dt=pd.Timestamp("2026-11-26 09:00"),type="HW",height_m=2.0)])
        with patch.object(app,"station_row",return_value=SimpleNamespace(timezone_id="America/Punta_Arenas")),patch.object(tide_engine,"TIDES",frame):
            result=app.tide_events("TEST","2026-11-26T12:00:00+00:00",1)
            self.assertEqual(result["start_local"],"2026-11-26T09:00:00")
            self.assertEqual(len(result["events"]),1)

class PublishedStationTests(unittest.TestCase):
    def test_kirke_reference(self):
        result=app.kirke_reference_qa()
        self.assertTrue(result["pass"],str(result))
    def test_white_gap_diagnostics(self):
        g=app.EVENTS[app.EVENTS.station_id=="CUR010"].sort_values("local_dt").reset_index(drop=True)
        tested=0
        for i in range(len(g)-1):
            a,b=g.iloc[i],g.iloc[i+1]
            if "WEAK_VARIABLE" not in (a.event_type,b.event_type):
                continue
            midpoint=a.local_dt+(b.local_dt-a.local_dt)/2
            result=app.current_diagnostic("CUR010",midpoint.to_pydatetime())
            self.assertIsNone(result["current"]["intensity_kn"])
            self.assertIsNotNone(result["previous_event"])
            self.assertIsNotNone(result["next_event"])
            tested+=1
        self.assertGreater(tested,0)
    def test_long_gap_blocks_interpolation(self):
        frame=CurrentSafetyTests().sample()
        frame.loc[1,"local_dt"]=pd.Timestamp("2026-11-27 12:00")
        with patch.object(app,"EVENTS",frame),patch.object(app,"station_row"):
            result=app.instant("TEST",datetime(2026,11,27,4))
            self.assertIsNone(result["intensity_kn"])
            self.assertEqual(result["status"],"SOURCE_GAP_REVIEW_REQUIRED")
        import integrated_services
        with patch.object(integrated_services,"EVENTS",frame):
            self.assertEqual(integrated_services._model_threshold_windows("TEST",datetime(2026,11,26,23),24,2.5),[])
    def test_inglesa_restored_slack(self):
        r=app.instant("CUR009",datetime.fromisoformat("2026-08-31T22:01"))
        self.assertEqual(r["event_type"],"SLACK")
        self.assertEqual(r["intensity_kn"],0)
    def test_mackinlay_restored_slacks(self):
        for stamp in ["2026-02-01T00:04","2026-04-01T00:10"]:
            r=app.instant("CUR021",datetime.fromisoformat(stamp))
            self.assertEqual(r["event_type"],"SLACK")
            self.assertEqual(r["intensity_kn"],0)
    def test_white_restored_slacks(self):
        for stamp in ["2026-01-31T22:07","2026-03-31T22:54"]:
            r=app.instant("CUR010",datetime.fromisoformat(stamp))
            self.assertEqual(r["event_type"],"SLACK")
            self.assertEqual(r["intensity_kn"],0)
    def test_quesahuen_restored_events(self):
        for stamp,kind,kn in [
            ("2026-01-31T15:29","SLACK",0),("2026-01-31T17:06","MAX_EBB",4.1),
            ("2026-01-31T19:10","SLACK",0),("2026-01-31T23:41","MAX_FLOOD",2.8),
            ("2026-03-31T15:40","SLACK",0),("2026-03-31T17:13","MAX_EBB",4.1),
            ("2026-03-31T20:02","SLACK",0),("2026-04-01T00:03","MAX_FLOOD",2.6),
            ("2026-08-31T22:23","SLACK",0),("2026-08-31T23:06","MAX_FLOOD",1.0),
            ("2026-09-01T00:03","MAX_FLOOD",0.4),("2026-10-31T20:26","SLACK",0),
            ("2026-10-31T22:41","MAX_EBB",3.1)]:
            r=app.instant("CUR007",datetime.fromisoformat(stamp))
            self.assertEqual(r["event_type"],kind)
            self.assertEqual(r["intensity_kn"],kn)
        g=app.EVENTS[app.EVENTS.station_id=="CUR007"].sort_values("local_dt")
        self.assertFalse(g.local_dt.duplicated().any())
        self.assertLessEqual(g.local_dt.diff().max(),pd.Timedelta(hours=12))
    def test_long_gap_report(self):
        for sid in ("CUR007","CUR021"):
            g=app.EVENTS[app.EVENTS.station_id==sid].sort_values("local_dt").reset_index(drop=True)
            gaps=g.local_dt.diff().dt.total_seconds()/3600
            for i in gaps[gaps>12].index:
                a,b=g.iloc[i-1],g.iloc[i]
                print("LONG_GAP",sid,a.local_dt,a.event_type,b.local_dt,b.event_type,round(gaps[i],3))
            self.assertGreater(len(g),0)

if __name__=="__main__":
    unittest.main()
