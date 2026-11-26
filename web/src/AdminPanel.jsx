import React,{useEffect,useState} from "react";
export default function AdminPanel({base,token,onExpired}){
 const [data,setData]=useState(null),[error,setError]=useState("");
 useEffect(()=>{const c=new AbortController();let active=true;
 setData(null);setError("");
 (async()=>{try{const u=new URL("/admin/summary",base);const res=await fetch(u,{headers:{Authorization:"Bearer "+token},cache:"no-store",redirect:"error",signal:c.signal});if(!active)return;if(res.status===401){onExpired();return}if(!res.ok)throw Error("Acceso administrativo no disponible");const result=await res.json();if(active)setData(result)}catch(e){if(active)setError(e.message)}})();
 return()=>{active=false;c.abort()};
 },[base,token,onExpired]);
 const fields=[["verified_accounts","Usuarios verificados"],["active_trials","Pruebas activas"],["paid_accounts","Suscriptores de pago"],["approved_ledger_clp","Pagos aprobados (CLP)"],["review_notifications","Incidencias"]];
 return <section className="estoa-account"><h2>Administración ESTOA</h2>{error?<p role="alert">{error}</p>:!data?<p role="status">Consultando…</p>:<div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(140px,1fr))",gap:12}}>{fields.map(([k,label])=><article key={k}><small>{label}</small><h3>{typeof data[k]==="number"?data[k].toLocaleString("es-CL"):"—"}</h3></article>)}</div>}<p>Pagos aprobados no equivalen a ingresos netos.</p></section>
}
