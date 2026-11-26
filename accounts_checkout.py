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
