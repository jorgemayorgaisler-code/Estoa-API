const CACHE='estoa-v3';
const SHELL=['/'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)))});
self.addEventListener('activate',e=>e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;
 const u=new URL(e.request.url);
 // API data must never be served stale from the PWA cache.
 if(u.hostname==='estoa-api.onrender.com'){e.respondWith(fetch(e.request));return}
 // App shell/assets: network first, cached fallback for temporary loss of connectivity.
 e.respondWith(fetch(e.request).then(r=>{if(r.ok){let x=r.clone();caches.open(CACHE).then(c=>c.put(e.request,x))}return r}).catch(()=>caches.match(e.request)));
});
