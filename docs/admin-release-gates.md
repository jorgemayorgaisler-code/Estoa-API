# Administrative release gates

Admin routes must remain unmounted until second-factor verification is implemented.
Preferred design: WebAuthn using a maintained library, exact HTTPS origin and RP ID,
single-use challenges, user verification required, session-bound elevation with a
provisional ten-minute maximum lifetime. Do not enable a password-only fallback.
Enrollment and recovery must be separately authorized. Test revocation, replay,
wrong origin, expiry, disabled accounts and password changes.

The current dashboard reports aggregate database state, not accounting records.
Monthly payment totals are grouped by service period start in America/Santiago,
not settlement date. Refund and chargeback totals describe current ledger status.
Historical conversion and retention require durable, deduplicated lifecycle events
and explicit cohort definitions. Do not infer historical conversion from active
subscriptions or use current state to reconstruct historical revenue.

Before enabling: verify the chosen library and deployment origin, implement and
test MFA, audit access, test aggregate counts with fixtures, and review privacy.
No production activation or paid infrastructure is authorized by this document.
