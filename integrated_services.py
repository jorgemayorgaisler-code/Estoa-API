
import pandas as pd, json
from pathlib import Path
from app import EVENTS, REG
ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
if not (DATA/"current_method_registry.csv").exists(): DATA=ROOT
METHODS=pd.read_csv(DATA/"current_method_registry.csv")
WEAK=pd.read_csv(DATA/"weak_tables_A_G.csv")

def _nearest_minutes(table,max_kn,threshold,case):
    x=WEAK[(WEAK.table==table)&(WEAK.threshold_kn==threshold)&(WEAK.case==case)].copy()
    if x.empty: return None
    d=(x.max_intensity_kn-max_kn).abs(); m=d.min(); ties=x[d==m]
    # Midpoint tie semantics are not source-verified: do not guess.
    if len(ties)!=1: return None
    return int(ties.iloc[0].minutes)

def _model_threshold_windows(station_id, start, hours, threshold):
    """Calculated crossings of the continuous current model; not PUB3015 empirical table values."""
    import math
    if not (0 <= threshold <= 10):
        return []
    s=pd.Timestamp(start)
    e=s+pd.Timedelta(hours=hours)
    g=EVENTS[EVENTS.station_id==station_id].sort_values("local_dt").reset_index(drop=True)
    intervals=[]
    maxima={"MAX_FLOOD","MAX_EBB"}
    for i in range(len(g)-1):
        a,b=g.iloc[i],g.iloc[i+1]
        if not ((a.event_type=="SLACK" and b.event_type in maxima) or
                (a.event_type in maxima and b.event_type=="SLACK")):
            continue
        maximum=b if a.event_type=="SLACK" else a
        if pd.isna(maximum.intensity_kn):
            continue
        speed=abs(float(maximum.intensity_kn))
        if speed<=0:
            continue
        duration=b.local_dt-a.local_dt
        if duration<=pd.Timedelta(0):
            continue
        ratio=min(1.0,threshold/speed)
        if a.event_type=="SLACK":
            fraction=2*math.asin(ratio)/math.pi
            lo,hi=a.local_dt,a.local_dt+duration*fraction
        else:
            fraction=2*math.acos(ratio)/math.pi
            lo,hi=a.local_dt+duration*fraction,b.local_dt
        if hi>=s and lo<=e:
            intervals.append((max(lo,s),min(hi,e)))
    intervals.sort()
    merged=[]
    for lo,hi in intervals:
        if merged and lo<=merged[-1][1]+pd.Timedelta(seconds=1):
            merged[-1]=(merged[-1][0],max(merged[-1][1],hi))
        else:
            merged.append((lo,hi))
    return [{"start":lo.isoformat(),"end":hi.isoformat(),
             "threshold_kn":threshold,"method":"CALCULATED_CONTINUOUS",
             "source":"ESTOA_CURRENT_MODEL","case":"continuous"}
            for lo,hi in merged if hi>lo]


def weak_windows(station_id,start,hours=24,threshold=1.0):
    mr=METHODS[METHODS.station_id==station_id].iloc[0]
    supported=set(float(x) for x in str(mr.empirical_thresholds_kn).split(',') if x.strip())
    if not any(abs(float(threshold)-x)<1e-6 for x in supported):
        return _model_threshold_windows(station_id,start,hours,float(threshold))
    g=EVENTS[EVENTS.station_id==station_id].sort_values("local_dt").reset_index(drop=True)
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
        if we>s and ws<e:
            # Query bounds are applied consistently to empirical and model windows.
            # Preserve the untrimmed SHOA-derived interval for auditing.
            clipped_start=max(ws,s); clipped_end=min(we,e)
            if clipped_end<=clipped_start: continue
            out.append({"start":clipped_start.isoformat(),"end":clipped_end.isoformat(),
                        "full_start":ws.isoformat(),"full_end":we.isoformat(),"center":c.isoformat(),
                        "threshold_kn":threshold,"table":mr.weak_current_table,"case":case,
                        "method":"PUB3015_EMPIRICAL_TABLE",
                        "source":"PUB3015_2026_WEAK_CURRENT_TABLE_"+str(mr.weak_current_table)})
    # Preserve source-level intervals; report overlap explicitly rather than
    # silently merging distinct SHOA cases or implying independent windows.
    out.sort(key=lambda w: (w["start"], w["end"]))
    furthest_end = None
    for window in out:
        lo, hi = pd.Timestamp(window["start"]), pd.Timestamp(window["end"])
        window["overlaps_previous"] = bool(furthest_end is not None and lo < furthest_end)
        furthest_end = hi if furthest_end is None else max(furthest_end, hi)
    return out

def weak_windows_diagnostics(station_id, start, hours=24, threshold=1.0):
    """Return explicit availability and overlap diagnostics without inventing data."""
    if station_id not in set(METHODS.station_id):
        raise ValueError("Unknown current station")
    import math
    if not math.isfinite(float(threshold)) or not (0 <= float(threshold) <= 10) or not (1 <= hours <= 168):
        raise ValueError("Invalid query range")
    windows = weak_windows(station_id, start, hours, threshold)
    registry_row = METHODS[METHODS.station_id == station_id].iloc[0]
    empirical_thresholds = {
        float(value) for value in str(registry_row.empirical_thresholds_kn).split(",")
        if value.strip()
    }
    # Provenance describes the selected calculation path, even when no windows
    # were produced (e.g. insufficient events or an unresolved table lookup).
    method = ("PUB3015_EMPIRICAL_TABLE"
              if any(abs(float(threshold) - value) < 1e-6 for value in empirical_thresholds)
              else "CALCULATED_CONTINUOUS")
    return {
        "station_id": station_id, "threshold_kn": float(threshold),
        "method": method, "windows": windows,
        "overlap_count": sum(bool(w.get("overlaps_previous")) for w in windows),
        "has_windows": bool(windows),
        "empty_result_note": (
            None if windows else
            "No windows returned. This does not establish that no navigable period exists; "
            "table lookup gaps and event coverage must be reviewed."
        ),
        "operational_notice": "Planning estimate only; verify official SHOA data and observed conditions."
    }

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
