"""Internal reconciliation; never grant paid access from preapproval status alone."""
from accounts_store import connection
from accounts_payments import fetch_subscription, LAUNCH_PRICE_CLP

def reconcile_subscription(provider_id, event_id):
    if not provider_id or not event_id:
        raise ValueError("Missing identifiers")
    with connection() as conn:
        row=conn.execute("SELECT account_id,amount_clp FROM subscriptions WHERE provider_id=%s FOR UPDATE",(provider_id,)).fetchone()
        if not row:
            raise LookupError("Unknown subscription")
        event=conn.execute("INSERT INTO payment_webhook_events(provider_event_id) VALUES (%s) ON CONFLICT DO NOTHING RETURNING provider_event_id",(event_id,)).fetchone()
        if not event:
            return "duplicate"
        data=fetch_subscription(provider_id)
        recurring=data.get("auto_recurring") or {}
        if str(data.get("id"))!=provider_id or str(data.get("external_reference"))!=str(row["account_id"]):
            raise ValueError("Subscription identity mismatch")
        if recurring.get("currency_id")!="CLP" or recurring.get("transaction_amount")!=row["amount_clp"] or row["amount_clp"]!=LAUNCH_PRICE_CLP or recurring.get("frequency")!=1 or recurring.get("frequency_type")!="months":
            raise ValueError("Subscription terms mismatch")
        status=data.get("status")
        if status not in {"pending","authorized","paused","cancelled","expired"}:
            raise ValueError("Unknown provider status")
        conn.execute("""UPDATE subscriptions SET status=%s,verified_at=now(),
            access_until=CASE WHEN %s='authorized' THEN access_until ELSE NULL END
            WHERE provider_id=%s""",(status,status,provider_id))
        return status
