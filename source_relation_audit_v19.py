import fitz, csv, json, math, calendar
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
ROOT=Path(__file__).resolve().parent
PDF=Path('/mnt/data/PUB 3009 ENERO 2026 tablas de marea.pdf')
DATA=ROOT/'data'
# Parse Bahia Orange Table I, PDF pages 145-148, 3 months/page, two half-month columns/month.
doc=fitz.open(PDF)
rows=[]
time_x=[93.9,175.0,257.0,337.0,418.0,500.0]
for page_no in range(145,149):
    page=doc[page_no-1]
    words=page.get_text('words')
    base_month=(page_no-145)*3+1
    for ci,x in enumerate(time_x):
        month=base_month+ci//2
        half=ci%2
        maxday=calendar.monthrange(2026,month)[1]
        for w in words:
            x0,y0,x1,y1,t,*_=w
            if abs(x0-x)>1.8 or not (len(t)==4 and t.isdigit()) or not (100<y0<730): continue
            idx=int((y0-103.9)//39.45)+1
            day=idx + (15 if half else 0)
            if day<1 or day>maxday: continue
            # nearest height on same baseline at x+~29
            hs=[]
            for h in words:
                hx,hy,_,_,ht,*_=h
                if abs(hy-y0)<1.2 and abs(hx-(x+29.2))<3.5:
                    try: hs.append(float(ht.replace(',','.')))
                    except: pass
            if not hs: continue
            rows.append({'source_date':f'2026-{month:02d}-{day:02d}','source_time':t,'height_m':hs[0]})
# dedupe and sort
seen={}
for r in rows: seen[(r['source_date'],r['source_time'])]=r
rows=list(seen.values())
rows.sort(key=lambda r: datetime.strptime(r['source_date']+r['source_time'],'%Y-%m-%d%H%M'))
# classify extrema by adjacent heights
for i,r in enumerate(rows):
    h=r['height_m']
    hp=rows[i-1]['height_m'] if i else None
    hn=rows[i+1]['height_m'] if i+1<len(rows) else None
    if hp is not None and hn is not None: r['type']='HW' if h>=hp and h>=hn else 'LW'
    elif hn is not None: r['type']='HW' if h>hn else 'LW'
    else: r['type']='HW' if h>hp else 'LW'
out=DATA/'pub3009_pattern_bahia_orange_2026.csv'
pd.DataFrame(rows)[['source_date','source_time','height_m','type']].to_csv(out,index=False)

# Verified Table II relation registry from visual/geometric source audit.
registry=[
 dict(station_id='CUR003',station_name='Canal Dalcahue',pattern_port='Puerto Montt',capability='EVENT_TIMES_ONLY',hw_time_rule='+00:27',lw_time_rule='+00:27',hw_height_rule='MISSING',lw_height_rule='MISSING',source_page=185,verification_status='VERIFIED',notes='Row 570 lies under PUERTO PATRÓN PUERTO MONTT; blank height columns remain missing.'),
 dict(station_id='CUR007',station_name='Paso Quesahuén',pattern_port='Bahía Orange',capability='FULL_TIDE',hw_time_rule='-02:00',lw_time_rule='-01:58',hw_height_rule='ADD +0.62',lw_height_rule='ADD -0.35',source_page=187,verification_status='VERIFIED',notes='Row 717 continues the BAHÍA ORANGE pattern section from the preceding page until the next pattern heading.'),
 dict(station_id='CUR009',station_name='Angostura Inglesa',pattern_port='Angostura Inglesa',capability='FULL_TIDE',hw_time_rule='+00:00',lw_time_rule='+00:00',hw_height_rule='PATTERN',lw_height_rule='PATTERN',source_page=187,verification_status='VERIFIED',notes='Pattern port; Table I reference pages 103-106.'),
 dict(station_id='CUR010',station_name='Angostura White',pattern_port='Puerto Natales',capability='FULL_TIDE',hw_time_rule='-00:29',lw_time_rule='-00:39',hw_height_rule='LINEAR 0.53*x+0.23',lw_height_rule='LINEAR 0.53*x+0.23',source_page=188,verification_status='VERIFIED',notes='Parenthesized correction is a linear relation per Table II Note 2; one expression spans the height correction field and applies to the secondary-port height.'),
 dict(station_id='CUR011',station_name='Angostura Kirke',pattern_port='Puerto Natales',capability='FULL_TIDE',hw_time_rule='-02:05',lw_time_rule='-02:05',hw_height_rule='ADD +0.00',lw_height_rule='ADD +0.05',source_page=188,verification_status='VERIFIED',notes='Row 860 under Puerto Natales section.'),
 dict(station_id='CUR016',station_name='Segunda Angostura',pattern_port='Puerto Montt',capability='FULL_TIDE',hw_time_rule='-03:05',lw_time_rule='-03:05',hw_height_rule='ADD -0.73',lw_height_rule='ADD +0.12',source_page=190,verification_status='VERIFIED',notes='Row 1130 lies under PUERTO PATRÓN PUERTO MONTT; supersedes prior transformed data that used Bahía Gregorio.'),
 dict(station_id='CUR018',station_name='Bahía Posesión',pattern_port='Punta Delgada',capability='FULL_TIDE',hw_time_rule='-00:23',lw_time_rule='-00:56',hw_height_rule='ADD +1.21',lw_height_rule='ADD -0.01',source_page=190,verification_status='VERIFIED',notes='Row 1080 under Punta Delgada.'),
 dict(station_id='CUR019',station_name='Punta Wreck',pattern_port='Puerto Montt',capability='FULL_TIDE',hw_time_rule='-05:10',lw_time_rule='-05:02',hw_height_rule='MULTIPLY 1.91',lw_height_rule='MULTIPLY 2.46',source_page=189,verification_status='VERIFIED',notes='Asterisk denotes multiplicative height factor per Table II Note 1.'),
]
pd.DataFrame(registry).to_csv(ROOT/'PUB3009_SOURCE_RELATION_REGISTRY_v19.csv',index=False)

# update JSON rules
rules=json.load(open(DATA/'tide_rules_pub3009_current_stations_v1.json'))
for r in rules:
    if r['station_id']=='CUR003': r['pattern']='Puerto Montt'
    if r['station_id']=='CUR007': r['pattern']='Bahía Orange'
    if r['station_id']=='CUR016': r['pattern']='Puerto Montt'
json.dump(rules,open(DATA/'tide_rules_pub3009_current_stations_v1.json','w'),ensure_ascii=False,indent=2)

patterns={
 'Puerto Montt':'pub3009_pattern_puerto_montt_2026.csv','Castro':'pub3009_pattern_castro_2026.csv',
 'Puerto Chacabuco':'pub3009_pattern_puerto_chacabuco_2026.csv','Angostura Inglesa':'pub3009_pattern_angostura_inglesa_2026.csv',
 'Puerto Natales':'pub3009_pattern_puerto_natales_2026.csv','Bahía Gregorio':'pub3009_pattern_bahia_gregorio_2026.csv',
 'Punta Delgada':'pub3009_pattern_punta_delgada_2026.csv','Bahía Orange':'pub3009_pattern_bahia_orange_2026.csv'}
# local publication time adjustment: CUR005-CUR022 +1h in 2026; CUR003 stays source UTC-4 display basis.
local_plus={f'CUR{i:03d}':(60 if i>=5 else 0) for i in range(1,23)}
def hm(s):
    sign=-1 if s.startswith('-') else 1
    s=s.lstrip('+-'); h,m=map(int,s.split(':')); return sign*(h*60+m)
def height(rule,h):
    if rule=='MISSING': return None
    if rule=='PATTERN': return h
    if rule.startswith('ADD '): return h+float(rule.split()[1])
    if rule.startswith('MULTIPLY '): return h*float(rule.split()[1])
    if rule.startswith('LINEAR '):
        expr=rule.split(' ',1)[1].replace('x','*h'); return eval(expr,{'__builtins__':{}},{'h':h})
    raise ValueError(rule)
allout=[]
for rr in registry:
    sid=rr['station_id']; pat=rr['pattern_port']; df=pd.read_csv(DATA/patterns[pat],dtype={'source_time':str})
    for _,x in df.iterrows():
        typ=x['type']; off=hm(rr['hw_time_rule'] if typ=='HW' else rr['lw_time_rule']) + local_plus[sid]
        src=datetime.strptime(str(x['source_date'])+str(x['source_time']).zfill(4),'%Y-%m-%d%H%M')
        loc=src+timedelta(minutes=off)
        hr=rr['hw_height_rule'] if typ=='HW' else rr['lw_height_rule']
        hv=height(hr,float(x['height_m']))
        allout.append(dict(station_id=sid,local_datetime=loc.isoformat(),type=typ,height_m=None if hv is None else round(hv,4),pattern_port=pat,pattern_source_datetime=src.isoformat(),pattern_height_m=float(x['height_m'])))
tides=pd.DataFrame(allout).sort_values(['station_id','local_datetime'])
tides.to_csv(DATA/'pub3009_tide_events_current_stations_2026.csv',index=False)
# QA
qa=[]
for sid,g in tides.groupby('station_id'):
    g=g.sort_values('local_datetime'); dt=pd.to_datetime(g.local_datetime); gaps=dt.diff().dt.total_seconds().dropna()/3600
    alt=all(a!=b for a,b in zip(g.type.iloc[:-1],g.type.iloc[1:]))
    cap=registry[[x['station_id'] for x in registry].index(sid)]['capability']
    hp=(g.height_m.isna().all() if cap=='EVENT_TIMES_ONLY' else g.height_m.notna().all())
    qa.append(dict(station_id=sid,events=len(g),chronology=dt.is_monotonic_increasing,alternation=alt,height_policy=hp,min_gap_h=round(gaps.min(),3),max_gap_h=round(gaps.max(),3),pass_all=dt.is_monotonic_increasing and alt and hp))
pd.DataFrame(qa).to_csv(ROOT/'QA_TIDE_SOURCE_RELATIONS_v19.csv',index=False)
# specific assertions
assert len(rows)>1300 and len(rows)<1500
assert all(x['pass_all'] for x in qa)
# Kirke reference remains corrected
from importlib.machinery import SourceFileLoader
te=SourceFileLoader('te',str(ROOT/'tide_engine.py')).load_module()
k=te.tide_at('CUR011','2026-10-04T18:30:00')
assert k['display_height_m']==0.25 and k['next']['time_local'].startswith('2026-10-04T19:20')
summary={'version':'v19','status':'PASS','bahia_orange_pattern_events':int(len(rows)),'transformed_events':int(len(tides)),'relations_verified':int(len(registry)),'qa_stations_pass':int(sum(bool(x['pass_all']) for x in qa)),'qa_stations_total':int(len(qa)),'corrected_relations':['CUR003 pattern Castro -> Puerto Montt','CUR007 transformed source Puerto Chacabuco -> Bahía Orange','CUR016 transformed source Bahía Gregorio -> Puerto Montt'],'kirke_reference_2026_10_04_1830':k}
json.dump(summary,open(ROOT/'QA_SOURCE_RELATION_AUDIT_v19.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
