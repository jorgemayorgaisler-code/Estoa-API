# Private preview
Use accounts_preview:app in an isolated environment. Do not mount public calculation routes in that service.
The private transport must never fall back to public endpoints. Keep session token in memory, clear data on logout and account change, cancel in-flight requests, and exclude authenticated responses from service worker caches.
Before connecting the full navigation UI, provide an authenticated station catalog and explicit preview origin configuration. Verify CORS, account verification delivery, session expiry, and all routes on mobile.
Production remains unchanged. No infrastructure or payment activation authorized by this change.
