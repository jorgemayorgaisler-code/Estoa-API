"""Internal checkout reservation. Ambiguous provider outcomes require reconciliation."""
import uuid
from accounts_store import connection

def reserve_checkout(account_id):
    with connection() as conn:
        account=conn.execute("SELECT id,email FROM accounts WHERE id=%s AND email_verified_at IS NOT NULL AND disabled_at IS NULL FOR UPDATE",(account_id,)).fetchone()
        if not account:
            raise PermissionError("Account unavailable")
        existing=conn.execute("SELECT provider_id FROM subscriptions WHERE account_id=%s AND status IN ('pending','authorized','paused')",(account_id,)).fetchone()
        if existing:
            raise PermissionError("Existing subscription")
        row=conn.execute("INSERT INTO checkout_reservations(account_id,request_id,status) VALUES (%s,%s,'reserved') ON CONFLICT(account_id) DO NOTHING RETURNING request_id",(account_id,uuid.uuid4())).fetchone()
        if not row:
            raise PermissionError("Checkout already reserved; reconcile before retry")
        return row["request_id"],account["email"]


def start_checkout(account_id, consent):
    from accounts_payments import create_pending_subscription, LAUNCH_PRICE_CLP
    from urllib.parse import urlparse
    if consent is not True:
        raise PermissionError("Explicit consent required")
    request_id,email=reserve_checkout(account_id)
    try:
        data=create_pending_subscription(account_id,email)
        provider_id=data.get("id")
        url=data.get("init_point","")
        parsed=urlparse(url)
        if not provider_id or data.get("status")!="pending" or str(data.get("external_reference"))!=str(account_id):
            raise ValueError("Unexpected subscription response")
        if parsed.scheme!="https" or parsed.hostname not in {"www.mercadopago.cl","www.mercadopago.com","www.mercadopago.com.ar"} or parsed.username or parsed.password:
            raise ValueError("Unexpected checkout URL")
        with connection() as conn:
            conn.execute("INSERT INTO subscriptions(provider_id,account_id,status,amount_clp) VALUES (%s,%s,'pending',%s)",(provider_id,account_id,LAUNCH_PRICE_CLP))
            row=conn.execute("UPDATE checkout_reservations SET provider_id=%s,status='bound' WHERE account_id=%s AND request_id=%s AND status='reserved' RETURNING request_id",(provider_id,account_id,request_id)).fetchone()
            if not row:
                raise RuntimeError("Reservation changed")
        return {"checkout_url":url}
    except Exception:
        with connection() as conn:
            conn.execute("UPDATE checkout_reservations SET status='review_required' WHERE account_id=%s AND request_id=%s AND status='reserved'",(account_id,request_id))
        raise
