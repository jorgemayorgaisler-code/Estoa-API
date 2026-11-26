import React,{useState,useEffect} from "react";
import {usePrivateCatalog} from "./usePrivateCatalog.js";
import {createPrivateApi} from "./privateApi.js";
export default function PrivateNavigation({base,token,onExpired}){
 const catalog=usePrivateCatalog(base,token,onExpired);
 const [sid,setSid]=useState(""),[mode,setMode]=useState("now"),[moment,setMoment]=useState(""),[result,setResult]=useState(null),[error,setError]=useState("");
 const [query,setQuery]=useState(null);
 useEffect(()=>{setResult(null);setError("");if(!query||!token)return;
 const controller=new AbortController();let active=true;
 Promise.resolve().then(()=>createPrivateApi(base,token,()=>{if(active)onExpired()})(query.path,query.params,{signal:controller.signal})).then(data=>{if(active)setResult(data)}).catch(e=>{if(active)setError(e.message)});
 return()=>{active=false;controller.abort()};
 },[query,base,token,onExpired]);
 const included=catalog?.stations?.filter(s=>s.included)||[];
 return <section className="page"><h3>Navegación privada · pruebas</h3>{catalog?.error&&<p>{catalog.error}</p>}
 <label>Estación<select value={sid} onChange={e=>{setSid(e.target.value);setQuery(null);setResult(null)}}><option value="">Seleccionar</option>{catalog?.stations?.map(s=><option key={s.station_id} value={s.station_id} disabled={!s.included}>{s.station_name}{s.included?"":" · Premium"}</option>)}</select></label>
 <label>Consulta<select value={mode} onChange={e=>{setMode(e.target.value);setQuery(null);setResult(null)}}><option value="now">Ahora</option><option value="moment">Calcular momento</option><option value="forecast">Próximamente</option></select></label>
 {mode!=="now"&&<label>Fecha y hora local de la estación<input type="datetime-local" value={moment} onChange={e=>{setMoment(e.target.value);setQuery(null);setResult(null)}}/></label>}
 <button disabled={!included.some(s=>s.station_id===sid)||(mode!=="now"&&!moment)} onClick={()=>setQuery(mode==="now"?{path:"/conditions/now",params:{station_id:sid}}:mode==="moment"?{path:"/conditions/at",params:{station_id:sid,local_datetime:moment}}:{path:"/forecast",params:{station_id:sid,start:moment,hours:24}})}>Consultar</button>
 {error&&<p role="alert">{error}</p>}{result&&<pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{JSON.stringify(result,null,2)}</pre>}<p>Vista técnica de pruebas; no usar para navegación.</p></section>
}
