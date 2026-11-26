import React,{useState,useEffect} from "react";
import PrivateCurve from "./PrivateCurve.jsx";
import {usePrivateCatalog} from "./usePrivateCatalog.js";
import {createPrivateApi} from "./privateApi.js";
function duration(start,end){
 const a=Date.parse(start+"Z"),b=Date.parse(end+"Z");
 const minutes=Math.round((b-a)/60000);
 return Number.isFinite(minutes)&&minutes>=0?Math.floor(minutes/60)+" h "+minutes%60+" min":"No disponible";
}
export default function PrivateNavigation({base,token,onExpired}){
 const catalog=usePrivateCatalog(base,token,onExpired);
 const [sid,setSid]=useState(""),[mode,setMode]=useState("now"),[moment,setMoment]=useState(""),[rawResult,setResult]=useState(null),[error,setError]=useState("");
 const [query,setQuery]=useState(null),[threshold,setThreshold]=useState("1");
 const permitted=!!catalog?.stations?.some(s=>s.station_id===sid&&s.included);
 const result=permitted?rawResult:null;
 useEffect(()=>{if(!permitted){setQuery(null);setResult(null)}},[permitted]);
 useEffect(()=>{setResult(null);setError("");if(!query||!token||!permitted)return;
 const controller=new AbortController();let active=true;
 Promise.resolve().then(()=>createPrivateApi(base,token,()=>{if(active)onExpired()})(query.path,query.params,{signal:controller.signal})).then(data=>{if(active)setResult(data)}).catch(e=>{if(active)setError(e.message)});
 return()=>{active=false;controller.abort()};
 },[query,base,token,onExpired,permitted]);
 const included=catalog?.stations?.filter(s=>s.included)||[];
 return <section className="page"><h3>Navegación privada · pruebas</h3>{catalog?.error&&<p>{catalog.error}</p>}
 <label>Estación<select value={sid} onChange={e=>{setSid(e.target.value);setQuery(null);setResult(null)}}><option value="">Seleccionar</option>{catalog?.stations?.map(s=><option key={s.station_id} value={s.station_id} disabled={!s.included}>{s.station_name}{s.included?"":" · Premium"}</option>)}</select></label>
 <label>Consulta<select value={mode} onChange={e=>{setMode(e.target.value);setQuery(null);setResult(null)}}><option value="now">Ahora</option><option value="moment">Calcular momento</option><option value="forecast">Próximamente</option><option value="weak">Ventanas de corriente</option><option value="current">Curva de corriente</option><option value="tide">Curva de marea</option><option value="sun">Orto y ocaso</option></select></label>
 {mode!=="now"&&<label>Fecha y hora local de la estación<input type="datetime-local" value={moment} onChange={e=>{setMoment(e.target.value);setQuery(null);setResult(null)}}/></label>}
 {mode==="weak"&&<label>Corriente máxima (kn)<input type="number" min="0" max="10" step="0.1" value={threshold} onChange={e=>{setThreshold(e.target.value);setQuery(null);setResult(null)}}/></label>}
 <button disabled={(mode==="weak"&&(threshold===""||Number(threshold)<0||Number(threshold)>10))||!included.some(s=>s.station_id===sid)||(mode!=="now"&&!moment)} onClick={()=>setQuery(mode==="now"?{path:"/conditions/now",params:{station_id:sid}}:mode==="moment"?{path:"/conditions/at",params:{station_id:sid,local_datetime:moment}}:mode==="weak"?{path:"/weak-windows",params:{station_id:sid,start:moment,hours:24,threshold_kn:threshold}}:mode==="current"?{path:"/current-curve",params:{station_id:sid,start:moment,hours:24,interval_minutes:30}}:mode==="tide"?{path:"/tide-curve",params:{station_id:sid,start:moment,hours:12}}:mode==="sun"?{path:"/sun-events",params:{station_id:sid,local_date:moment.slice(0,10)}}:{path:"/forecast",params:{station_id:sid,start:moment,hours:24}})}>Consultar</button>
 {error&&<p role="alert">{error}</p>}{result?.current&&<article className="info-card"><small>Corriente prevista</small><strong>{Number.isFinite(result.current.intensity_kn)?result.current.intensity_kn.toFixed(2)+" kn":"No disponible"}</strong><p>Fase: {({FLOOD:"Llenante",EBB:"Vaciante",SLACK:"Estoa",VARIABLE:"Débil o variable"})[result.current.phase]||"No determinada"}</p><p>Tendencia: {({INCREASING:"Aumentando",DECREASING:"Disminuyendo",EVENT:"Evento publicado"})[result.current.trend]||"No determinada"}</p><p>Dirección: {Number.isFinite(result.current.direction_true)?result.current.direction_true+"° V":"No disponible"}</p><p>Marea: {Number.isFinite(result.tide?.height_m)?result.tide.height_m.toFixed(2)+" m":"No disponible"}</p><p>{result.query?.local_datetime}</p></article>}{Array.isArray(result?.samples)&&(mode==="tide"||mode==="current")&&<PrivateCurve samples={result.samples} field={mode==="tide"?"height_m":"intensity_kn"} unit={mode==="tide"?"m":"kn"}/>}{Array.isArray(result?.windows)&&<section><h3>Ventanas previstas · {result.threshold_kn} kn</h3>{result.windows.length===0?<p>No se encontraron ventanas; esto no demuestra ausencia de periodos navegables.</p>:result.windows.map((w,i)=><article className="info-card" key={i}><strong>{w.start?.replace("T"," ")} — {w.end?.replace("T"," ")}</strong><p>Duración en hora local: {duration(w.start,w.end)}</p><p>{w.method==="PUB3015_EMPIRICAL_TABLE"?"Tabla empírica PUB 3015":w.method==="CALCULATED_CONTINUOUS"?"Estimación continua del modelo":"Método: "+(w.method||"no informado")}</p>{w.overlaps_previous&&<p>Se superpone con una ventana anterior.</p>}</article>)}<p>Hora local. Verificar publicación oficial y condiciones observadas.</p></section>}{result&&<pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{JSON.stringify(result,null,2)}</pre>}<p>Vista técnica de pruebas; no usar para navegación.</p></section>
}
