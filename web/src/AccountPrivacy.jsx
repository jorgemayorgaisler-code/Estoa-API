import React,{useState,useEffect,useRef} from "react";
export default function AccountPrivacy({apiBase,token,onExpired}){
 const [status,setStatus]=useState(null),[password,setPassword]=useState(""),[consent,setConsent]=useState(false),[message,setMessage]=useState(""),[busy,setBusy]=useState(false);
 const pending=useRef(null);
 async function request(method,body,signal){
  const base=new URL(apiBase);
  if(base.protocol!=="https:"||base.username||base.password||base.search||base.hash||base.pathname!=="/")throw Error("Servicio no disponible.");
  const response=await fetch(base.origin+"/accounts/me/deletion-request",{method,signal,cache:"no-store",redirect:"error",headers:{Authorization:"Bearer "+token,"Content-Type":"application/json"},...(body?{body:JSON.stringify(body)}:{})});
  if(signal.aborted)return null;
  if(response.status===401){onExpired();throw Error("Sesión vencida.");}
  if(!response.ok)throw Error(response.status===429?"Demasiados intentos.":"Solicitud no disponible.");
  return response.json();
 }
 useEffect(()=>{
  const c=new AbortController();pending.current=c;
  request("GET",null,c.signal).then(data=>{if(!c.signal.aborted)setStatus(data)}).catch(e=>{if(!c.signal.aborted)setMessage(e.message)});
  return ()=>pending.current?.abort();
 },[apiBase,token]);
 async function submit(e){
  e.preventDefault();if(busy||!consent||!status||status.request)return;
  const c=new AbortController();pending.current=c;setBusy(true);setMessage("");
  try{const data=await request("POST",{password},c.signal);if(!c.signal.aborted)setStatus({request:data});}
  catch(e){if(!c.signal.aborted)setMessage(e.message)}
  finally{if(!c.signal.aborted){setBusy(false);setPassword("");setConsent(false)}}
 }
 const labels={pending_review:"Pendiente de revisión",billing_review:"Revisión de suscripción y pagos",completed:"Completada",rejected:"Rechazada"};
 return <article><h3>Privacidad y eliminación de cuenta</h3>
 <p>La solicitud no cancela automáticamente los cobros ni elimina inmediatamente tus datos.</p>
 {status?.request?<p>Estado: {labels[status.request.status]||"En revisión"}</p>:status&&<form onSubmit={submit}>
 <label>Contraseña actual<input type="password" autoComplete="current-password" required minLength={12} maxLength={128} value={password} onChange={e=>setPassword(e.target.value)}/></label>
 <label><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>Confirmo que deseo solicitar la eliminación de mi cuenta.</label>
 <button disabled={busy||!consent}>Enviar solicitud</button></form>}
 <p role="status">{message}</p></article>
}
