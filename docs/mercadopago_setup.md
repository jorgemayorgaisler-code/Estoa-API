# ESTOA — Mercado Pago Chile subscription rollout

**Status: foundation only; charging is disabled until credentials, a price, account binding and verified server-side entitlement are deployed.**

The server-side module `payments_mercadopago.py` prepares a **monthly CLP** subscription using Mercado Pago's `POST /preapproval` API and returns a secure checkout URL. It never grants access when creating a pending subscription.

## Required before public launch

1. Confirm commercial price in CLP and whether the merchant account is eligible for recurring subscriptions.
2. Create Mercado Pago developer application and obtain private access token. Store only in Render secret environment variables, never in the frontend or Git.
3. Configure `MERCADOPAGO_ACCESS_TOKEN` and `ESTOA_PREMIUM_PRICE_CLP`.
4. Implement authenticated user accounts and persistent binding of user ID to Mercado Pago `preapproval.id`. Never accept a user ID or email from an unauthenticated public checkout request.
5. Implement authenticated backend checkout endpoint with rate limiting, CSRF protections as applicable, and idempotent handling.
6. Register Mercado Pago webhook notifications, validate authenticity, and **fetch subscription status server-to-server** via `GET /preapproval/{id}` before changing entitlements. Handle authorized, pending, paused, canceled and failed payments; define grace-period policy.
7. Persist subscriptions, payment audit events, access expiry and revocation; reconcile periodically.
8. Test sandbox and production edge cases (declined card, duplicate notifications, canceled plan, network failures), then enable checkout explicitly.

**Do not expose the payment token or activate premium on checkout redirect alone.**

Official API: https://www.mercadopago.cl/developers/es/reference/online-payments/subscriptions/overview
