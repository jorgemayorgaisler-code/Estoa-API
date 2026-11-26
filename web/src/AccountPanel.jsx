import React, {useState,useEffect} from "react";
import "./AccountPanel.css";

export default function AccountPanel({apiBase, stations=[]}) {
  const [mode,setMode]=useState("login");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [token,setToken]=useState("");
  const [trial,setTrial]=useState(null);
  const [status,setStatus]=useState(null);
  const [now,setNow]=useState(Date.now());
  const [station,setStation]=useState("");
  const [message,setMessage]=useState("");
  const [busy,setBusy]=useState(false);
  const [consent,setConsent]=useState(false);
  async function request(path,body,method="POST"){
    const response=await fetch(apiBase.replace(/\/$/,"")+"/accounts/"+path,{
      method,headers:{"Content-Type":"application/json",...(token?{Authorization:"Bearer "+token}:{})},
      ...(body?{body:JSON.stringify(body)}:{})
    });
    if(!response.ok) throw Error(response.status===429?"Demasiados intentos. Intenta más tarde.":"No se pudo completar la solicitud.");
    return response.status===204?null:response.json();
  }
  useEffect(()=>{
    if(!token){setStatus(null);return;}
    let cancelled=false;
    const refresh=async()=>{
      try{const data=await request("me",null,"GET");if(!cancelled)setStatus(data)}
      catch(e){if(!cancelled)setMessage(e.message)}
    };
    refresh();
    const timer=setInterval(()=>{setNow(Date.now());refresh()},60000);
    return ()=>{cancelled=true;clearInterval(timer)};
  },[token]);
  const expiry=status?.expires_at||trial?.expires_at;
  const days=expiry?Math.max(0,Math.ceil((Date.parse(expiry)-now)/86400000)):0;
  async function run(fn){
    setBusy(true);setMessage("");
    try{await fn()}catch(e){setMessage(e.message)}finally{setBusy(false)}
  }
  return <section className="estoa-account">
    <h2>Mi cuenta ESTOA</h2>
    {!token?<form onSubmit={e=>{e.preventDefault();run(async()=>{
      const data=await request(mode,{email,password});
      setPassword("");
      if(mode==="login")setToken(data.access_token);
      else setMessage("Revisa tu correo para verificar tu cuenta.");
    })}}>
      <h3>{mode==="login"?"Iniciar sesión":"Crear cuenta"}</h3>
      <label>Correo electrónico<input type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label>
      <label>Contraseña<input type="password" minLength={12} maxLength={128} autoComplete={mode==="login"?"current-password":"new-password"} required value={password} onChange={e=>setPassword(e.target.value)}/></label>
      <button disabled={busy}>{mode==="login"?"Ingresar":"Registrarme"}</button>
      <button type="button" disabled={busy} onClick={()=>{setMode(mode==="login"?"register":"login");setPassword("");setMessage("")}}>{mode==="login"?"Crear cuenta":"Ya tengo cuenta"}</button>
    </form>:<>
      <label>Estación gratuita<select value={station} onChange={e=>setStation(e.target.value)}><option value="">Seleccionar</option>{stations.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
      <button disabled={busy||!station} onClick={()=>run(async()=>{await request("me/free-station",{station_id:station});setStatus(await request("me",null,"GET"));setMessage("Estación seleccionada.")})}>Confirmar estación permanente</button>
      <button disabled={busy} onClick={()=>run(async()=>{await request("logout");setToken("");setTrial(null)})}>Cerrar sesión</button>
    </>}
    <article className="estoa-premium"><h3>ESTOA Premium</h3><strong>Primer mes gratis</strong><p>$990 CLP al mes después, si decides suscribirte.</p><p>Todas las estaciones. Sin cobro automático.</p>
      {token&&<button disabled={busy||!!trial||!!status?.activated_at} onClick={()=>run(asyncasync()=>{setTrial(await request("me/trial"));setStatus(await request("me",null,"GET"))})}>Activar mes gratuito</button>}
      {token&&status?.plan==="free"&&import.meta.env.VITE_PAYMENT_PREVIEW==="true"&&<><label><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/>Acepto contratar Premium por $990 CLP mensuales mediante Mercado Pago.</label><button disabled={busy||!consent} onClick={()=>run(async()=>{const data=await request("me/checkout",{consent:true});const url=new URL(data.checkout_url);if(url.protocol!=="https:"||!["www.mercadopago.cl","www.mercadopago.com","www.mercadopago.com.ar"].includes(url.hostname))throw Error("Enlace de pago inválido");window.location.assign(url.href)})}>Contratar Premium</button></>}
      {status&&<p>Plan vigente: {status.plan==="premium"?"Premium":"Free"}</p>}
      {expiry&&<p>{days>0?"Periodo gratuito: "+days+" días restantes. ":"Periodo gratuito finalizado. "}Vencimiento: {new Date(expiry).toLocaleString("es-CL",{timeZone:"America/Santiago"})}</p>}
    </article>
    <p role="status" aria-live="polite">{message}</p>
  </section>
}
