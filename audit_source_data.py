"""Read-only audit of ESTOA source data. Run: python audit_source_data.py"""
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data" if (ROOT/"data"/"national_master.csv").exists() else ROOT
events=pd.read_csv(DATA/"national_master.csv",dtype={"source_time":str})
reg=pd.read_csv(DATA/"station_registry.csv")
times=events.source_time.str.replace(r"\.0$","",regex=True).str.zfill(4)
dt=pd.to_datetime(events.source_date.astype(str)+" "+times.str[:2]+":"+times.str[2:],errors="coerce")
speed=pd.to_numeric(events.intensity_kn,errors="coerce")
direction=pd.to_numeric(events.direction_true,errors="coerce")
maxima=events.event_type.isin(["MAX_FLOOD","MAX_EBB"])
def valid_zone(z):
    try:
        ZoneInfo(str(z))
        return True
    except Exception:
        return False
a,b=ROOT/"station_registry.csv",ROOT/"data"/"station_registry.csv"
report={
    "active_data_directory":str(DATA.relative_to(ROOT)),
    "event_count":len(events),
    "station_count":int(reg.station_id.nunique()),
    "registry_duplicate_ids":int(reg.station_id.duplicated(keep=False).sum()),
    "registry_copies_byte_identical":a.read_bytes()==b.read_bytes() if a.exists() and b.exists() else None,
    "unknown_station_events":int((~events.station_id.isin(reg.station_id)).sum()),
    "invalid_event_times":int(dt.isna().sum()),
    "duplicate_station_times":int(pd.DataFrame({"station":events.station_id,"time":dt}).duplicated(keep=False).sum()),
    "invalid_maxima":int((maxima & (~np.isfinite(speed) | (speed<0))).sum()),
    "invalid_nonnull_directions":int((events.direction_true.notna() & (~np.isfinite(direction) | (direction<0) | (direction>360))).sum()),
    "invalid_coordinates":int((~pd.to_numeric(reg.latitude,errors="coerce").between(-90,90) | ~pd.to_numeric(reg.longitude,errors="coerce").between(-180,180)).sum()),
    "invalid_timezones":reg.loc[~reg.timezone_id.map(valid_zone),"station_id"].tolist(),
    "unknown_event_types":sorted(events.event_type.dropna().loc[~events.event_type.isin(["SLACK","MAX_FLOOD","MAX_EBB","WEAK_VARIABLE"])].unique().tolist()),
    "coverage_by_station":{}
}
for station,g in pd.DataFrame({"station":events.station_id,"time":dt}).groupby("station"):
    t=g.time.dropna().sort_values()
    report["coverage_by_station"][str(station)]={"first":str(t.min()),"last":str(t.max()),"events":len(g),"largest_gap_hours":float(t.diff().max().total_seconds()/3600) if len(t)>1 else None}
# Targeted source comparison: PUB3015 2026 pp. 47–48.
reference=[("2026-01-31","1429","SLACK",0),("2026-01-31","1606","MAX_EBB",4.1),("2026-01-31","1810","SLACK",0),("2026-01-31","2241","MAX_FLOOD",2.8),("2026-03-31","1440","SLACK",0),("2026-03-31","1613","MAX_EBB",4.1),("2026-03-31","1902","SLACK",0),("2026-03-31","2303","MAX_FLOOD",2.6)]
report["quesahuen_source_comparison"]=[]
for day,hhmm,kind,kn in reference:
    stamp=pd.Timestamp(day+" "+hhmm[:2]+":"+hhmm[2:])
    rows=events.loc[(events.station_id=="CUR007") & (dt==stamp)]
    report["quesahuen_source_comparison"].append({"source_datetime":str(stamp),"expected_type":kind,"expected_kn":kn,"matching_timestamp_count":len(rows),"actual":rows[["event_type","intensity_kn","direction_true"]].fillna("").to_dict("records")})
print(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
