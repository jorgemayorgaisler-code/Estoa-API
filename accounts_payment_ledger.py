"""Internal ledger reconciliation; provider payment ingestion remains disabled."""
from accounts_store import connection

def refresh_paid_access(provider_id):
    with connection() as conn:
        row=conn.execute("SELECT status FROM subscriptions WHERE provider_id=%s FOR UPDATE",(provider_id,)).fetchone()
        if not row:
            raise LookupError("Unknown subscription")
        period=conn.execute("""SELECT max(period_end) AS expiry FROM subscription_payments
            WHERE provider_id=%s AND status='approved' AND currency='CLP'
            AND amount_clp=(SELECT amount_clp FROM subscriptions WHERE provider_id=%s)
            AND period_start<=now() AND period_end>now()""",(provider_id,provider_id)).fetchone()
        expiry=period["expiry"] if row["status"]=="authorized" else None
        conn.execute("UPDATE subscriptions SET access_until=%s WHERE provider_id=%s",(expiry,provider_id))
        return expiry
