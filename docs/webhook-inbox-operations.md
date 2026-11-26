# Inbox processing
The receiver stores only signed resource and request identifiers. It does not yet classify resource types or grant access.
Before enabling sandbox delivery, validate actual provider headers, event types and retry behavior. A worker must resolve the resource against authoritative provider endpoints; never trust an unsigned topic to grant access.
Use transactional claims with expiring leases, bounded retries, and review state. Reconcile verified payment and entitlement atomically. A request identifier alone is not a payment idempotency key: deduplicate authoritative payment IDs and billing periods.
Keep ESTOA_WEBHOOK_PREVIEW disabled until worker, classification, sandbox fixtures and monitoring are ready.
