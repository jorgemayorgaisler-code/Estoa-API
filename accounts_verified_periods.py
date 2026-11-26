"""Internal boundary only. Never call with unverified provider evidence."""
from datetime import datetime,timedelta
from accounts_store import connection

def record_verified_period(provider_id,payment_id,amount,start,end):
    if not provider_id or not payment_id or not isinstance(start,datetime) or not isinstance(end,datetime) or start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError("Explicit verified period required")
    if not timedelta(days=27)<=end-start<=timedelta(days=32):
        raise ValueError("Unexpected monthly period")
    with connection() as conn:
        sub=conn.execute("SELECT amount_clp,status FROM subscriptions WHERE provider_id=%s FOR UPDATE",(provider_id,)).fetchone()
        if not sub or sub["amount_clp"]!=amount or sub["status"]!="authorized":
            raise ValueError("Subscription mismatch")
        overlap=conn.execute("""SELECT 1 FROM subscription_payments WHERE provider_id=%s AND provider_payment_id<>%s AND status='approved' AND period_start<%s AND period_end>%s""",(provider_id,payment_id,end,start)).fetchone()
        if overlap:
            raise ValueError("Overlapping approved period")
        row=conn.execute("""INSERT INTO subscription_payments(provider_payment_id,provider_id,amount_clp,currency,period_start,period_end,status)
            VALUES (%s,%s,%s,'CLP',%s,%s,'approved') ON CONFLICT DO NOTHING RETURNING provider_payment_id""",(payment_id,provider_id,amount,start,end)).fetchone()
        if not row:
            old=conn.execute("SELECT provider_id,amount_clp,period_start,period_end,status FROM subscription_payments WHERE provider_payment_id=%s",(payment_id,)).fetchone()
            if not old or (old["provider_id"],old["amount_clp"],old["period_start"],old["period_end"])!=(provider_id,amount,start,end):
                raise ValueError("Payment or period conflict")
        return _refresh(conn,provider_id)

def _refresh(conn,provider_id):
    return conn.execute("""UPDATE subscriptions s SET access_until=CASE WHEN s.status='authorized' THEN
        (SELECT max(period_end) FROM subscription_payments p WHERE p.provider_id=s.provider_id
         AND p.status='approved' AND p.amount_clp=s.amount_clp AND p.currency='CLP'
         AND p.period_start<=now() AND p.period_end>now()) ELSE NULL END
         WHERE s.provider_id=%s RETURNING access_until""",(provider_id,)).fetchone()["access_until"]

def revoke_verified_payment(provider_id,payment_id,status):
    if status not in ("refunded","charged_back"):
        raise ValueError("Invalid revocation status")
    with connection() as conn:
        if not conn.execute("SELECT provider_id FROM subscriptions WHERE provider_id=%s FOR UPDATE",(provider_id,)).fetchone():
            raise LookupError("Unknown subscription")
        if not conn.execute("""UPDATE subscription_payments SET status=%s,verified_at=now()
            WHERE provider_id=%s AND provider_payment_id=%s RETURNING provider_payment_id""",(status,provider_id,payment_id)).fetchone():
            raise LookupError("Unknown payment")
        return _refresh(conn,provider_id)
