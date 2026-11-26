"""Explicit maintenance operations; no scheduler or public endpoint."""
from accounts_store import connection

def prune_auth_records():
    with connection() as conn:
        return {table:conn.execute(sql).rowcount for table,sql in (
            ("sessions","DELETE FROM account_sessions WHERE expires_at < now()-interval '7 days'"),
            ("verification","DELETE FROM email_verification_tokens WHERE expires_at < now()-interval '7 days'"),
            ("reset","DELETE FROM password_reset_tokens WHERE expires_at < now()-interval '7 days'"),
            ("rate_limits","DELETE FROM auth_rate_limits WHERE window_start < now()-interval '2 hours'"))}

def operational_counts():
    with connection() as conn:
        return conn.execute("""SELECT
            (SELECT count(*) FROM accounts WHERE email_verified_at IS NOT NULL AND disabled_at IS NULL) AS verified_accounts,
            (SELECT count(*) FROM account_sessions WHERE revoked_at IS NULL AND expires_at>now()) AS active_sessions,
            (SELECT count(*) FROM payment_webhook_inbox WHERE state='pending') AS pending_notifications,
            (SELECT count(*) FROM payment_webhook_inbox WHERE state='review') AS review_notifications""").fetchone()
