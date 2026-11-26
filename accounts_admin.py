from accounts_store import connection

def admin_summary(account_id):
    with connection() as conn:
        row=conn.execute("""SELECT a.id FROM accounts a JOIN account_admin_grants g ON g.account_id=a.id
            WHERE a.id=%s AND a.disabled_at IS NULL AND a.email_verified_at IS NOT NULL AND g.revoked_at IS NULL
            FOR SHARE OF a,g""",(account_id,)).fetchone()
        if not row:
            raise PermissionError("Administrative access required")
        return conn.execute("""SELECT
            (SELECT count(*) FROM accounts WHERE email_verified_at IS NOT NULL AND disabled_at IS NULL) AS verified_accounts,
            (SELECT count(*) FROM premium_trials WHERE activated_at<=now() AND expires_at>now()) AS active_trials,
            (SELECT count(DISTINCT account_id) FROM subscriptions WHERE status='authorized' AND access_until>now()) AS paid_accounts,
            (SELECT COALESCE(sum(amount_clp),0) FROM subscription_payments WHERE status='approved') AS approved_ledger_clp,
            (SELECT count(*) FROM payment_webhook_inbox WHERE state='review') AS review_notifications""").fetchone()
