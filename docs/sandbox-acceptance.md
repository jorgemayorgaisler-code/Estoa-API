# Sandbox acceptance
Provider endpoint paths and response fields remain provisional until verified against official documentation and actual sandbox responses.
Use isolated PostgreSQL and preview services, never production credentials. Configure secrets through Render, not GitHub or chat.
Capture redacted fixtures for subscription, recurring invoice, payment, refund and chargeback. Verify merchant, account linkage, currency, amount, payment identity and authoritative billing boundaries. Never infer a paid period from notification arrival.
Test replay, out-of-order events, duplicate billing periods, expired worker leases, failed requests, future periods and partial refunds. Confirm paid-through cancellation policy and future-period activation before release.
Keep checkout and webhook flags disabled until acceptance. No real charge or paid infrastructure authorized.
