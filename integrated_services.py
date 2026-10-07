
import pandas as pd, json
from pathlib import Path
from app import EVENTS, REG
DATA=Path(__file__).resolve().parent/"data"
METHODS=pd.read_csv(DATA/"current_method_registry.csv")
WEAK=pd.read_csv(DATA/"weak_tables_A_G.csv")

def _nearest_minutes(table,max_kn,threshold,case):
    x=WEAK[(WEAK.table==table)&(WEAK.threshold_kn==threshold)&(WEAK.case==case)].copy()
    if x.empty: return None
    d=(x.max_intensity_kn-max_kn).abs(); m=d.min(); ties=x[d==m]
    # Midpoint tie semantics are not source-verified: do not guess.
    if len(ties)!=1: return None
    return int(ties.iloc[0].minutes)

def weak_windows(station_id,start,hours=24,threshold=1.0):
    g=EVENTS[EVENTS.station_id==station_id].sort_values("local_dt").reset_index(drop=True)
    mr=METHODS[METHODS.station_id==station_id].iloc[0]
    s=pd.Timestamp(start); e=s+pd.Timedelta(hours=hours); out=[]
    for i,r in g.iterrows():
        c=r.local_dt
        if c<s-pd.Timedelta(hours=6) or c>e+pd.Timedelta(hours=6): continue
        case=None
        if r.event_type=="SLACK" and bool(mr.supports_slack_case_i): case="i"
        elif r.event_type=="WEAK_VARIABLE" and bool(mr.supports_weak_variable_case_ii): case="ii"
        elif r.event_type in ("MAX_FLOOD","MAX_EBB") and pd.notna(r.intensity_kn) and r.intensity_kn<=threshold and bool(mr.supports_lower_intensity_case_iii): case="iii"
        if not case: continue
        pm=g.iloc[:i]; pm=pm[pm.event_type.isin(["MAX_FLOOD","MAX_EBB"])]
        nm=g.iloc[i+1:]; nm=nm[nm.event_type.isin(["MAX_FLOOD","MAX_EBB"])]
        if pm.empty or nm.empty: continue
        a,b=pm.iloc[-1],nm.iloc[0]
        before=_nearest_minutes(mr.weak_current_table,float(a.intensity_kn),threshold,case)
        after=_nearest_minutes(mr.weak_current_table,float(b.intensity_kn),threshold,case)
        if before is None or after is None: continue
        ws=c-pd.Timedelta(minutes=before); we=c+pd.Timedelta(minutes=after)
        if we>=s and ws<=e:
            out.append({"start":ws.isoformat(),"end":we.isoformat(),"center":c.isoformat(),
                        "threshold_kn":threshold,"table":mr.weak_current_table,"case":case})
    return out

def tide_capability(station_id):
    r=REG[REG.station_id==station_id].iloc[0]
    cap=r.tide_automatic_capability
    return {"capability":cap,
            "height_available":cap=="FULL_TIDE",
            "event_times_available":cap in ("FULL_TIDE","EVENT_TIMES_ONLY"),
            "policy":"Never infer missing height corrections."}

def astronomy_policy(station_id):
    return {"role":"CONTEXT_ONLY","does_not_modify_current_prediction":True,
            "priority":["lunar_declination","syzygy_quadrature","perigee_apogee","phase"] if station_id=="CUR011"
                       else ["syzygy_quadrature","perigee_apogee","phase"]}
