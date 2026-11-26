# ESTOA accounts and subscriptions
Free accounts select one station; Premium accounts access all stations. Price: CLP 2990/month.
Keep existing public API unchanged until integration clients and migration are verified.
Use persistent PostgreSQL, unique normalized email, verified email before activation, Argon2id password hashes or managed identity, expiring revocable sessions, rate limits and password reset.
Enforce station entitlement server-side on every calculation and map endpoint; never rely on frontend hiding. Preserve a separate authenticated integration API policy.
Mercado Pago: create subscription server-side; never trust client payment status. Verify webhook signature and retrieve authoritative subscription status from provider; bind provider ID to account; process idempotently. No card data stored.
Keep secrets in Render environment variables, never in Git. Start in sandbox; no real charges until explicit production configuration.
Release gates: persistent database, auth and entitlement tests, webhook replay tests, mobile login tests, migration and rollback plan.
2027 data must be independently imported and validated; never extrapolate 2026 as 2027.
