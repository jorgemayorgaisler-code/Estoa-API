import {useEffect,useState} from "react";
import {createPrivateApi} from "./privateApi.js";
export function usePrivateCatalog(base,token,onExpired){
 const [result,setResult]=useState(null);
 useEffect(()=>{
  setResult(null);
  if(!token)return;
  let active=true,controller=null;
  const refresh=()=>{
   controller?.abort();
   const current=new AbortController();controller=current;
   Promise.resolve().then(()=>createPrivateApi(base,token,()=>{if(active&&!current.signal.aborted)onExpired()})("/stations",{},{signal:current.signal})).then(stations=>{
    if(!Array.isArray(stations))throw Error("Catálogo inválido");
    if(active&&!current.signal.aborted)setResult({token,base,stations});
   }).catch(e=>{if(active&&!current.signal.aborted)setResult({token,base,error:e.message})});
  };
  refresh();
  const timer=setInterval(refresh,30000);
  const visible=()=>{if(document.visibilityState==="visible")refresh()};
  document.addEventListener("visibilitychange",visible);
  return ()=>{active=false;controller?.abort();clearInterval(timer);document.removeEventListener("visibilitychange",visible)};
 },[base,token,onExpired]);
 return result?.token===token&&result?.base===base?result:null;
}
