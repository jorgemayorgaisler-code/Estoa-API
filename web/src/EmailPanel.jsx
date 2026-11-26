import React,{useState} from "react";
export default function EmailPanel({apiBase}){
 const [purpose,setPurpose]=useState("verification"),[email,setEmail]=useState(""),[token,setToken]=useState(""),[password,setPassword]=useState(""),[message,setMessage]=useState(""),[busy,setBusy]=useState(false);
 async function submit(action,body){
  setBusy(true);setMessage("");
  try{
   const base=new URL(apiBase);
   if(base.protocol!=="https:"||base.username||base.password)throw Error("Servidor inválido");
   const r=await fetch(new URL("/accounts/"+purpose+"/"+action,base),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body),cache:"no-store",redirect:"error"});
   if(!r.ok)throw Error(r.status===429?"Demasiados intentos. Intenta más tarde.":"No se pudo completar la solicitud.");
   setMessage(action==="request"?"Si corresponde, recibirás un código por correo.":"Operación completada. Puedes iniciar sesión.");
   if(action==="confirm"){setToken("");setPassword("")}
  }catch(e){setMessage(e.message)}finally{setBusy(false)}
 }
 return <section><h3>Verificación y recuperación</h3><label>Operación<select disabled={busy} value={purpose} onChange={e=>{setPurpose(e.target.value);setToken("");setPassword("");setMessage("")}}><option value="verification">Verificar correo</option><option value="reset">Recuperar contraseña</option></select></label>
 <form onSubmit={e=>{e.preventDefault();submit("request",{email})}}><label>Correo<input type="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label><button disabled={busy}>Solicitar código</button></form>
 <form onSubmit={e=>{e.preventDefault();submit("confirm",purpose==="reset"?{token:token.trim(),password}:{token:token.trim()})}}><label>Código recibido<input required autoComplete="off" minLength={43} maxLength={43} value={token} onChange={e=>setToken(e.target.value)}/></label>{purpose==="reset"&&<label>Nueva contraseña<input type="password" autoComplete="new-password" required minLength={12} maxLength={128} value={password} onChange={e=>setPassword(e.target.value)}/></label>}<button disabled={busy}>Confirmar</button></form><p role="status">{message}</p></section>
}
