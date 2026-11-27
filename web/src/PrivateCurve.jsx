import React from "react";
export default function PrivateCurve({samples,field,unit}){
 const values=samples.map(s=>s[field]).filter(Number.isFinite);
 if(!values.length)return <p>Sin datos disponibles.</p>;
 const low=Math.min(...values),high=Math.max(...values),span=high-low||1;
 const x=i=>40+i*320/Math.max(1,samples.length-1),y=v=>130-(v-low)*100/span;
 let path="",previous=false;
 samples.forEach((s,i)=>{const v=s[field];if(!Number.isFinite(v)){previous=false;return;}path+=(previous?" L":" M")+x(i)+" "+y(v);previous=true});
 return <figure><svg viewBox="0 0 380 160" width="100%" role="img" aria-label={"Curva prevista en "+unit}>
 <path d="M40 20 V130 H360" stroke="currentColor" opacity=".4" fill="none"/>
 <text x="2" y="30" fontSize="10" fill="currentColor">{high.toFixed(1)}</text><text x="2" y="130" fontSize="10" fill="currentColor">{low.toFixed(1)}</text>
 <path d={path} stroke="#1687bc" strokeWidth="2" fill="none"/>
 {samples.map((s,i)=>Number.isFinite(s[field])?<circle key={i} cx={x(i)} cy={y(s[field])} r="1.5" fill="#1687bc"/>:null)}
 <text x="40" y="150" fontSize="10" fill="currentColor">{samples[0]?.time_local?.slice(11,16)}</text><text x="330" y="150" fontSize="10" fill="currentColor">{samples.at(-1)?.time_local?.slice(11,16)}</text></svg><figcaption>{unit} · hora local · los vacíos indican datos no disponibles.</figcaption></figure>
}
