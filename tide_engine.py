
import math, pandas as pd
from pathlib import Path
DATA=Path(__file__).resolve().parent/"data"
TIDES=pd.read_csv(DATA/"pub3009_tide_events_current_stations_2026.csv")
TIDES["local_dt"]=pd.to_datetime(TIDES["local_datetime"])
def direct_height(p,n,t):
    a=(n.local_dt-p.local_dt).total_seconds(); e=(t-p.local_dt).total_seconds()
    return float(p.height_m)+(float(n.height_m)-float(p.height_m))*(1-math.cos(math.pi*e/a))/2
def tide_at(station_id,when):
    g=TIDES[TIDES.station_id==station_id].sort_values("local_dt")
    if g.empty:return {"available":False}
    t=pd.Timestamp(when)
    if t.tzinfo is not None:t=t.tz_localize(None)
    exact=g[g.local_dt==t]
    if len(exact):
        x=exact.iloc[0]; h=None if pd.isna(x.height_m) else round(float(x.height_m),3)
        return {"available":True,"height_m":h,"display_height_m":None if h is None else round(h,2),
                "trend":"EVENT","previous":None,"next":{"time_local":x.local_dt.isoformat(),"type":x.type,"height_m":h},
                "method":"PUB3009_PUBLISHED_EVENT"}
    a=g[g.local_dt<t]; b=g[g.local_dt>t]
    if a.empty or b.empty:return {"available":False,"reason":"OUT_OF_DATASET"}
    p=a.iloc[-1]; n=b.iloc[0]
    pe={"time_local":p.local_dt.isoformat(),"type":p.type,"height_m":None if pd.isna(p.height_m) else round(float(p.height_m),3)}
    ne={"time_local":n.local_dt.isoformat(),"type":n.type,"height_m":None if pd.isna(n.height_m) else round(float(n.height_m),3)}
    trend="RISING" if n.type=="HW" else "FALLING"
    if pd.isna(p.height_m) or pd.isna(n.height_m):
        return {"available":True,"height_m":None,"display_height_m":None,"trend":trend,
                "previous":pe,"next":ne,"method":"PUB3009_EVENT_TIMES_ONLY"}
    h=direct_height(p,n,t)
    return {"available":True,"height_m":round(h,3),"display_height_m":round(h,2),"trend":trend,
            "previous":pe,"next":ne,"method":"PUB3009_DIRECT_COSINE"}
