import React,{useState,useCallback} from "react";
import AccountPanel from "./AccountPanel.jsx";
import PrivateNavigation from "./PrivateNavigation.jsx";
import {usePrivateCatalog} from "./usePrivateCatalog.js";

export default function CommercialPreview(){
  const [token,setToken]=useState("");
  const [tab,setTab]=useState("account");
  const base=import.meta.env.VITE_ACCOUNTS_API;
  const expired=useCallback(()=>{setToken("");setTab("account")},[]);
  const changeSession=useCallback(value=>{setToken(value);setTab("account")},[]);
  let valid=false;
  try{const u=new URL(base);valid=u.protocol==="https:"&&!u.username&&!u.password&&!u.search&&!u.hash&&u.pathname==="/"&&u.hostname!=="estoa-api.onrender.com"}catch{}
  return valid?<CommercialContent base={base} token={token} tab={tab} setTab={setTab} expired={expired} changeSession={changeSession}/>:<main><h2>ESTOA · Pruebas comerciales</h2><p>Servidor privado no configurado.</p></main>;
}
function CommercialContent({base,token,tab,setTab,expired,changeSession}){
  const catalog=usePrivateCatalog(base,token,expired);
  const stations=(Array.isArray(catalog)?catalog:catalog?.stations||[]).map(s=>({id:s.station_id,name:s.station_name}));
  return <main><h2>ESTOA · Pruebas comerciales</h2>
    {token&&<div><button onClick={()=>setTab("account")}>Mi cuenta</button><button onClick={()=>setTab("navigation")}>Corrientes y mareas</button></div>}
    {token&&tab==="navigation"?<PrivateNavigation base={base} token={token} onExpired={expired}/>:<AccountPanel key={token||"guest"} apiBase={base} stations={stations} sessionToken={token} onSessionChange={changeSession}/>}
  </main>;
}
