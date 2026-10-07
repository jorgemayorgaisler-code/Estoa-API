import React,{useEffect,useState}from'react';import{createRoot}from'react-dom/client';import{Waves,Clock3,CalendarDays,Map,Menu}from'lucide-react';import'./style.css';
const API='https://estoa-api.onrender.com';
function App(){const[stations,setStations]=useState([]),[sid,setSid]=useState('CUR011'),[data,setData]=useState(null),[tab,setTab]=useState('Ahora');
useEffect(()=>{fetch(API+'/stations').then(r=>r.json()).then(setStations)},[]);
useEffect(()=>{if(tab!=='Ahora')return;let d=new Date(),local=new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,19);fetch(API+'/conditions/at?station_id='+sid+'&local_datetime='+local).then(r=>r.json()).then(setData)},[sid,tab]);
let c=data?.current,t=data?.tide;
return <main><header><div><b>ESTOA</b><small>CORRIENTES Y MAREAS · PATAGONIA CHILE</small></div><select value={sid} onChange={e=>setSid(e.target.value)}>{stations.map(s=><option key={s.station_id} value={s.station_id}>{s.station_name}</option>)}</select></header>
<section className="hero"><span>CONDICIÓN ACTUAL</span><h1>{c?.intensity_kn??'—'} <i>kn</i></h1><h2>{c?.phase==='EBB'?'REFLUJO':c?.phase==='FLOOD'?'FLUJO':c?.phase??'Cargando…'}</h2><p>{c?.direction_true!=null?Math.round(c.direction_true)+'° verdadero':'Dirección no disponible'} · {c?.trend==='DECREASING'?'disminuyendo':c?.trend==='INCREASING'?'aumentando':''}</p></section>
<div className="grid"><article><span>MAREA</span><strong>{t?.height_m!=null?Number(t.height_m).toFixed(2)+' m':'—'}</strong><p>{t?.trend??t?.state??'Según disponibilidad del punto'}</p></article><article><span>FUENTE</span><strong>PUB 3015</strong><p>Predicción astronómica 2026</p></article></div>
<section className="note">ESTOA presenta predicciones hidrográficas. Las condiciones reales pueden diferir de las predicciones publicadas.</section>
<nav>{[[Waves,'Ahora'],[Clock3,'Próximamente'],[CalendarDays,'Momento'],[Map,'Mapa'],[Menu,'Más']].map(([I,n])=><button className={tab===n?'on':''} onClick={()=>setTab(n)} key={n}><I size={21}/><small>{n}</small></button>)}</nav></main>}
createRoot(document.getElementById('root')).render(<App/>);