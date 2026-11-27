import React,{useState,useEffect,useRef} from "react";

export default function AccountSecurity({apiBase,token,onSignedOut}){
  const [mode,setMode]=useState("password");
  const [current,setCurrent]=useState("");
  const [next,setNext]=useState("");
  const [confirm,setConfirm]=useState("");
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState("");
  const pending=useRef(null);
  useEffect(()=>()=>pending.current?.abort(),[token,apiBase]);
  async function submit(e){
    e.preventDefault();
    if(busy)return;
    if(mode==="password"&&next!==confirm){setMessage("Las contraseñas nuevas no coinciden.");return;}
    const controller=new AbortController();
    pending.current=controller;
    setBusy(true);setMessage("");
    try{
      const base=new URL(apiBase);
      if(base.protocol!=="https:"||base.username||base.password||base.search||base.hash||base.pathname!=="/")throw Error("Servicio no disponible.");
      const response=await fetch(base.origin+"/accounts/me/"+(mode==="password"?"password":"sessions/revoke-all"),{
        method:"POST",cache:"no-store",redirect:"error",signal:controller.signal,
        headers:{"Content-Type":"application/json",Authorization:"Bearer "+token},
        body:JSON.stringify(mode==="password"?{current_password:current,new_password:next}:{password:current})
      });
      if(controller.signal.aborted)return;
      if(response.ok||response.status===401){onSignedOut();return;}
      setMessage(response.status===429?"Demasiados intentos. Intenta más tarde.":"No se pudo confirmar la operación.");
    }catch(e){if(!controller.signal.aborted)setMessage("No se pudo completar la operación.")}
    finally{if(!controller.signal.aborted){setCurrent("");setNext("");setConfirm("");setBusy(false)}}
  }
  return <article><h3>Seguridad de la cuenta</h3>
    <label>Operación<select disabled={busy} value={mode} onChange={e=>{setMode(e.target.value);setCurrent("");setNext("");setConfirm("");setMessage("")}}><option value="password">Cambiar contraseña</option><option value="logout">Cerrar sesión en todos los dispositivos</option></select></label>
    <form onSubmit={submit}>
      <p>Esta operación cerrará todas tus sesiones, incluida la actual.</p>
      <label>Contraseña actual<input required type="password" autoComplete="current-password" minLength={12} maxLength={128} value={current} onChange={e=>setCurrent(e.target.value)}/></label>
      {mode==="password"&&<><label>Nueva contraseña<input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={next} onChange={e=>setNext(e.target.value)}/></label><label>Repetir nueva contraseña<input required type="password" autoComplete="new-password" minLength={12} maxLength={128} value={confirm} onChange={e=>setConfirm(e.target.value)}/></label></>}
      <button disabled={busy}>Confirmar y cerrar sesiones</button>
    </form><p role="status">{message}</p>
  </article>
}
