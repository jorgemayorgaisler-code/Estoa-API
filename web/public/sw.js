const CACHE='estoa-v6';
const SHELL=['/'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('estoa-')&&k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;
 const u=new URL(e.request.url);
 // Never cache cross-origin API responses or external map tiles.
 if(u.origin!==self.location.origin)return;
 if(e.request.headers.has('Authorization')||u.pathname.startsWith('/private/')||u.pathname.startsWith('/accounts/'))return;
 if(e.request.mode==='navigate'){
   e.respondWith(fetch(e.request,{cache:'no-store'}).then(async r=>{if(r.ok){try{await (await caches.open(CACHE)).put(e.request,r.clone())}catch{}}return r}).catch(async()=>await caches.match(e.request)||await caches.match('/')||Response.error()));return;
 }
 if(!['script','style','image','font','manifest'].includes(e.request.destination))return;
 e.respondWith(fetch(e.request).then(async r=>{if(r.ok){try{await (await caches.open(CACHE)).put(e.request,r.clone())}catch{}}return r}).catch(async()=>await caches.match(e.request)||Response.error()));
});
