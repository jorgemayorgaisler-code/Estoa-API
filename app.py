
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import pandas as pd
from tide_engine import tide_at
import math

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
if not (DATA/"national_master.csv").exists(): DATA=ROOT
EVENTS=pd.read_csv(DATA/"national_master.csv", dtype={"source_time":str})
REG=pd.read_csv(DATA/"station_registry.csv")

EVENTS["source_time"]=EVENTS["source_time"].astype(str).str.replace(r"\.0$","",regex=True).str.zfill(4)
EVENTS["source_dt"]=pd.to_datetime(EVENTS["source_date"]+" "+EVENTS["source_time"].str[:2]+":"+EVENTS["source_time"].str[2:])
ADD1=set(REG.loc[REG["timezone_rule_2026"]=="PUB3015_PAGES_35_153_ADD_1H_2026","station_id"])
EVENTS["local_dt"]=EVENTS["source_dt"]+pd.to_timedelta(EVENTS["station_id"].isin(ADD1).astype(int),unit="h")
EVENTS=EVENTS.sort_values(["station_id","local_dt"]).reset_index(drop=True)

app=FastAPI(title="ESTOA API",version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])
MAX_TYPES={"MAX_FLOOD","MAX_EBB"}

def station_row(station_id):
    x=REG[REG.station_id==station_id]
    if x.empty: raise HTTPException(404,"Unknown station_id")
    return x.iloc[0]

def phase_of(event_type):
    return {"MAX_FLOOD":"FLOOD","MAX_EBB":"EBB","SLACK":"SLACK","WEAK_VARIABLE":"VARIABLE"}.get(event_type,"UNKNOWN")

def instant(station_id, dt):
    station_row(station_id)
    g=EVENTS[EVENTS.station_id==station_id].sort_values("local_dt").reset_index(drop=True)
    t=pd.Timestamp(dt.replace(tzinfo=None))
    exact=g[g.local_dt==t]
    if len(exact):
        e=exact.iloc[0]
        return {"status":"PUBLISHED_EVENT","intensity_kn":float(e.intensity_kn) if pd.notna(e.intensity_kn) else None,
                "phase":phase_of(e.event_type),"direction_true":float(e.direction_true) if pd.notna(e.direction_true) else None,
                "trend":"EVENT","event_type":e.event_type}
    prev=g[g.local_dt<t]
    nxt=g[g.local_dt>t]
    if prev.empty or nxt.empty: return {"status":"OUT_OF_DATASET","intensity_kn":None,"phase":"UNKNOWN","direction_true":None,"trend":"UNKNOWN"}
    a,b=prev.iloc[-1],nxt.iloc[0]
    if "WEAK_VARIABLE" in (a.event_type,b.event_type):
        return {"status":"WEAK_VARIABLE","intensity_kn":None,"phase":"VARIABLE","direction_true":None,"trend":"UNKNOWN"}
    standard=(a.event_type=="SLACK" and b.event_type in MAX_TYPES) or (a.event_type in MAX_TYPES and b.event_type=="SLACK")
    if not standard:
        return {"status":"NONSTANDARD_NO_VALUE","intensity_kn":None,"phase":"UNKNOWN","direction_true":None,"trend":"UNKNOWN"}
    dur=(b.local_dt-a.local_dt).total_seconds()
    f=(t-a.local_dt).total_seconds()/dur
    if a.event_type=="SLACK":
        val=float(b.intensity_kn)*math.sin(math.pi*f/2); ref=b
        trend="INCREASING"
    else:
        val=float(a.intensity_kn)*math.cos(math.pi*f/2); ref=a
        trend="DECREASING"
    return {"status":"CALCULATED_CONTINUOUS","intensity_kn":round(val,3),
            "phase":phase_of(ref.event_type),"direction_true":float(ref.direction_true) if pd.notna(ref.direction_true) else None,
            "trend":trend,"segment":{"from":a.event_type,"to":b.event_type}}

@app.get("/stations")
def stations():
    cols=["station_id","station_name","app_mode","tide_automatic_capability","weak_current_table","timezone_rule_2026","timezone_id","latitude","longitude","flow_direction_true","ebb_direction_true"]
    df=REG[cols].copy().astype(object)
    df=df.where(pd.notna(df),None)
    return df.to_dict("records")

@app.get("/conditions/at")
def conditions_at(station_id:str, local_datetime:datetime):
    r=station_row(station_id)
    return {"station":{"station_id":station_id,"name":r.station_name},
            "query":{"local_datetime":local_datetime.isoformat()},
            "current":instant(station_id,local_datetime),
            "tide":dict({"capability":r.tide_automatic_capability}, **tide_at(station_id,local_datetime)),
            "astronomy":{"role":"CONTEXT_ONLY"}}

@app.get("/conditions/now")
def conditions_now(station_id:str):
    # Server clock is intentionally explicit; mobile client should normally call /conditions/at
    # with the station-local time it wants displayed.
    return conditions_at(station_id,datetime.now())

@app.get("/forecast")
def forecast(station_id:str, start:datetime, hours:int=24):
    station_row(station_id)
    s=pd.Timestamp(start.replace(tzinfo=None)); e=s+pd.Timedelta(hours=hours)
    g=EVENTS[(EVENTS.station_id==station_id)&(EVENTS.local_dt>=s)&(EVENTS.local_dt<=e)].copy()
    out=[]
    for _,x in g.iterrows():
        out.append({"local_datetime":x.local_dt.isoformat(),"event_type":x.event_type,
                    "intensity_kn":float(x.intensity_kn) if pd.notna(x.intensity_kn) else None,
                    "direction_true":float(x.direction_true) if pd.notna(x.direction_true) else None})
    return {"station_id":station_id,"start":start.isoformat(),"hours":hours,"events":out}


@app.get("/weak-windows")
def weak_windows_endpoint(station_id:str, start:datetime, hours:int=24, threshold_kn:float=1.0):
    from integrated_services import weak_windows
    station_row(station_id)
    return {"station_id":station_id,"threshold_kn":threshold_kn,"windows":weak_windows(station_id,start,hours,threshold_kn)}

@app.get("/capabilities")
def capabilities(station_id:str):
    from integrated_services import tide_capability, astronomy_policy
    station_row(station_id)
    return {"station_id":station_id,"tide":tide_capability(station_id),"astronomy":astronomy_policy(station_id)}

@app.get("/qa/tide")
def tide_qa():
    import json
    return json.load(open(ROOT/"QA_NATIONAL_TIDE_v14.json", encoding="utf-8"))

@app.get("/tide-events")
def tide_events(station_id: str, start_local: str, hours: int = 24):
    import pandas as pd
    from tide_engine import TIDES
    start=pd.Timestamp(start_local)
    end=start+pd.Timedelta(hours=hours)
    g=TIDES[(TIDES.station_id==station_id)&(TIDES.local_dt>=start)&(TIDES.local_dt<=end)].sort_values("local_dt")
    events=[]
    for _,x in g.iterrows():
        h=None if pd.isna(x.height_m) else round(float(x.height_m),3)
        events.append({"time_local":x.local_dt.isoformat(),"type":x.type,"height_m":h})
    return {"station_id":station_id,"start_local":start.isoformat(),"hours":hours,"events":events}

@app.get("/qa/kirke-reference")
def kirke_reference_qa():
    """Regression check against the validated Kirke reference case."""
    dt=datetime(2026,10,4,18,30)
    got=instant("CUR011",dt)
    tide=tide_at("CUR011",dt)
    expected={"intensity_kn":4.899,"phase":"EBB","direction_true":290.0,"trend":"DECREASING","tide_height_m":0.248}
    checks={
        "intensity": got.get("intensity_kn") is not None and abs(got["intensity_kn"]-expected["intensity_kn"])<=0.002,
        "phase": got.get("phase")==expected["phase"],
        "direction": got.get("direction_true")==expected["direction_true"],
        "trend": got.get("trend")==expected["trend"],
        "tide_height": tide.get("height_m") is not None and abs(float(tide["height_m"])-expected["tide_height_m"])<=0.005,
    }
    return {"case":"CUR011_KIRKE_2026-10-04T18:30_LOCAL","pass":all(checks.values()),"checks":checks,"expected":expected,"actual":{"current":got,"tide":tide}}

@app.get("/qa/current-engine")
def current_engine_qa():
    """Structural regression QA over every published 2026 current event."""
    checks=[]
    for _,e in EVENTS.iterrows():
        got=instant(e.station_id,e.local_dt.to_pydatetime())
        ok_type=got.get("event_type")==e.event_type
        exp=None if pd.isna(e.intensity_kn) else float(e.intensity_kn)
        act=got.get("intensity_kn")
        ok_intensity=(exp is None and act is None) or (exp is not None and act is not None and abs(act-exp)<0.001)
        checks.append(ok_type and ok_intensity)
    return {"scope":"ALL_2026_PUBLISHED_CURRENT_EVENTS","stations":int(EVENTS.station_id.nunique()),"events":len(checks),"passed":sum(checks),"failed":len(checks)-sum(checks),"pass":all(checks)}

@app.get("/qa/interpolation")
def interpolation_qa():
    """Validate continuous sine/cosine interpolation at midpoints of standard segments."""
    tested=passed=0; failures=[]
    for sid,g in EVENTS.groupby("station_id"):
        g=g.sort_values("local_dt").reset_index(drop=True)
        for i in range(len(g)-1):
            a,b=g.iloc[i],g.iloc[i+1]
            standard=(a.event_type=="SLACK" and b.event_type in MAX_TYPES) or (a.event_type in MAX_TYPES and b.event_type=="SLACK")
            if not standard: continue
            mid=a.local_dt+(b.local_dt-a.local_dt)/2
            got=instant(sid,mid.to_pydatetime()); im=float(b.intensity_kn if a.event_type=="SLACK" else a.intensity_kn)
            expected=round(im*math.sqrt(0.5),3); tested+=1
            ok=got.get("intensity_kn") is not None and abs(got["intensity_kn"]-expected)<=0.001
            if ok: passed+=1
            elif len(failures)<10: failures.append({"station_id":sid,"midpoint":mid.isoformat(),"expected_kn":expected,"actual_kn":got.get("intensity_kn")})
    return {"scope":"MIDPOINTS_STANDARD_CURRENT_SEGMENTS","tested":tested,"passed":passed,"failed":tested-passed,"pass":tested==passed,"failures":failures}

@app.get("/health")
def health():
    return {"status":"ok","service":"ESTOA","edition":2026}

@app.get("/version")
def version():
    return {
        "app":"ESTOA",
        "api_version":"19",
        "edition":2026,
        "current_source":"PUB3015-2026",
        "tide_source":"PUB3009-2026"
    }
