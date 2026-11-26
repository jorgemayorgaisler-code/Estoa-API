from accounts_store import connection
from accounts_verified_periods import _refresh

def reconcile_due_periods(limit=100):
    if type(limit) is not int or not 1<=limit<=500:
        raise ValueError("Invalid batch size")
    with connection() as conn:
        rows=conn.execute("""SELECT s.provider_id FROM subscriptions s
            WHERE s.access_until IS DISTINCT FROM CASE WHEN s.status='authorized' THEN
            (SELECT max(p.period_end) FROM subscription_payments p WHERE p.provider_id=s.provider_id
             AND p.status='approved' AND p.currency='CLP' AND p.amount_clp=s.amount_clp
             AND p.period_start<=now() AND p.period_end>now()) ELSE NULL END
            ORDER BY s.provider_id LIMIT %s FOR UPDATE OF s SKIP LOCKED""",(limit,)).fetchall()
        for row in rows:
            _refresh(conn,row["provider_id"])
        return len(rows)
