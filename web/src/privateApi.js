const allowed=new Set(["/stations","/tide-curve","/current-curve","/sun-events","/current/diagnostic","/conditions/at","/conditions/now","/forecast","/weak-windows","/capabilities","/tide-events","/conditions/map"]);
export function createPrivateApi(base,token,onExpired=()=>{}){
  const origin=new URL(base);
  if(origin.protocol!=="https:"||origin.username||origin.password||origin.search||origin.hash||origin.pathname!=="/")throw Error("Servidor privado inválido");
  if(!token)throw Error("Inicia sesión");
  return async function request(path,params={},options={}){
    if(!allowed.has(path))throw Error("Consulta no autorizada");
    const url=new URL("/private"+path,origin);
    url.search=new URLSearchParams(params).toString();
    const response=await fetch(url,{method:"GET",headers:{Authorization:"Bearer "+token},cache:"no-store",redirect:"error",signal:options.signal});
    if(response.status===401){onExpired();throw Error("Sesión vencida");}
    if(response.status===403)throw Error("Estación no incluida en tu plan");
    if(!response.ok)throw Error("Consulta no disponible");
    return response.json();
  };
}
