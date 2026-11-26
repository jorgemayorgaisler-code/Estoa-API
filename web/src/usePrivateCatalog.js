import {useEffect,useState} from "react";
import {createPrivateApi} from "./privateApi.js";
export function usePrivateCatalog(base,token,onExpired){
 const [result,setResult]=useState(null);
 useEffect(()=>{
  setResult(null);
  if(!token)return;
  const controller=new AbortController();
  let active=true;
  Promise.resolve().then(()=>createPrivateApi(base,token,()=>{if(active)onExpired()})("/stations",{}, {signal:controller.signal})).then(stations=>{
   if(!Array.isArray(stations))throw Error("Catálogo inválido");
   if(active)setResult({token,base,stations});
  }).catch(e=>{if(active)setResult({token,base,error:e.message})});
  return ()=>{active=false;controller.abort()};
 },[base,token,onExpired]);
 return result?.token===token&&result?.base===base?result:null;
}
