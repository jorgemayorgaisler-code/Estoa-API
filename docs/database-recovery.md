# PostgreSQL backup and recovery — preview
No production database has been provisioned. Use a dedicated preview database and separate credentials.
Before migrations, obtain an encrypted backup using the provider's supported backup facility or pg_dump custom format. Never commit dumps, credentials or account data. Restrict access and record backup time and schema revision.
Restore into a separate empty database using pg_restore with exit-on-error. Do not restore over the running service. Verify migration history, /ready, row counts, foreign keys, account access, trial expiry and payment ledger reconciliation. Test revocation of restored sessions before reopening access.
Keep checkout and webhook processing disabled during restore; reconcile authoritative provider state before enabling either.
Record measured recovery time and data loss window. Retention, backup frequency, recovery objectives and provider costs require approval before production.
