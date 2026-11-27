import React,{useEffect,useState,useRef} from "react";
export default function AccountTerms({apiBase,token,onExpired}){
 const [doc,setDoc]=useState(null),[consent,setConsent]=useState(false),[busy,setBusy]=useState(false),[message,setMessage]=useState("");
 const pending=useRef(null);
 async function request(method,body,signal){
  const base=new URL(apiBase);
  if(base.protocol!=="https:"||base.username||base.password||base.search||base.hash||base.pathname!=="/")throw Error("Servicio no disponible.");
  const res=await fetch(base.origin+"/accounts/me/terms",{method,signal,cache:"no-store",redirect:"error",headers:{Authorization:"Bearer "+token,"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
  if(signal.aborted)return null;
  if(res.status===401){onExpired();throw Error("Sesión vencida.");}
  if(!res.ok)throw Error("Condiciones no disponibles o actualizadas. Vuelve a consultarlas.");
  return res.json();
 }
 async function load(){
  pending.current?.abort();const c=new AbortController();pending.current=c;
  setDoc(null);setConsent(false);setMessage("");setBusy(true);
  try{const data=await request("GET",null,c.signal);if(!c.signal.aborted){if(typeof data?.content!=="string"||!data.content||typeof data.version!=="string")throw Error("Documento no disponible.");setDoc(data)}}
  catch(e){if(!c.signal.aborted)setMessage(e.message)}
  finally{if(!c.signal.aborted)setBusy(false)}
 }
 useEffect(()=>{load();return ()=>pending.current?.abort()},[apiBase,token]);
 async function accept(e){
  e.preventDefault();if(!doc||!consent||busy)return;
  const c=new AbortController();pending.current=c;setBusy(true);setMessage("");
  try{const result=await request("POST",{version:doc.version,consent:true},c.signal);if(!c.signal.aborted){if(result?.version!==doc.version||!result.accepted_at)throw Error("Aceptación no confirmada.");setDoc({...doc,accepted_at:result.accepted_at});setConsent(false)}}
  catch(e){if(!c.signal.aborted){setDoc(null);setConsent(false);setMessage(e.message)}}
  finally{if(!c.signal.aborted)setBusy(false)}
 }
 return <article><h3>Términos y condiciones</h3>
 <button type="button" disabled={busy} onClick={load}>Consultar versión vigente</button>
 {doc&&<><p>Versión: {doc.version}</p><div style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere",maxHeight:"22rem",overflowY:"auto"}} tabIndex={0}>{doc.content}</div>
 {doc.accepted_at?<p>Condiciones aceptadas.</p>:<form onSubmit={accept}><label><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>He leído y acepto esta versión de las condiciones.</label><button disabled={busy||!consent}>Aceptar condiciones</button></form>}</>}
 <p role="status">{message}</p></article>
}
