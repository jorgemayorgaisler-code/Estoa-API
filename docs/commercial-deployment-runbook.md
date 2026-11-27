# Commercial preview deployment
Keep main and existing public services unchanged.
Provision a dedicated test PostgreSQL only after confirming cost, retention and authorization. Apply migrations 001–008 in order using a restricted migration identity. Back up before schema changes.
Deploy feature/accounts-foundation with uvicorn accounts_preview:app --host 0.0.0.0 --port $PORT and /health. Configure ESTOA_DATABASE_URL, ESTOA_RATE_LIMIT_SECRET and ESTOA_PREVIEW_ORIGIN as secrets/configuration. Never commit credentials.
Build separate static frontend with VITE_COMMERCIAL_PREVIEW=true and explicit HTTPS VITE_ACCOUNTS_API. Keep email, checkout and webhook flags off until their acceptance gates pass.
Verify unauthenticated requests, cross-account access, trial expiry, free station permanence, logout, mobile and cache behavior. Validate SMTP and sandbox provider independently.
Rollback by disabling preview flags and reverting preview deployment; preserve ledger and backups. Never roll back by deleting payment records.
Production launch requires public API migration, verified payment contract, operational worker, monitoring, backup/restore rehearsal and explicit approval.
