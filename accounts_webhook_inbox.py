from accounts_store import connection
from accounts_webhooks import verify_signature

def receive_notification(resource_id, request_id, signature):
    if not verify_signature(resource_id, request_id, signature):
        raise PermissionError("Invalid notification signature")
    with connection() as conn:
        row=conn.execute("""INSERT INTO payment_webhook_inbox(request_id,resource_id)
            VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING request_id""",
            (request_id,resource_id)).fetchone()
        if row:
            return "accepted"
        existing=conn.execute("SELECT resource_id FROM payment_webhook_inbox WHERE request_id=%s",(request_id,)).fetchone()
        if not existing or existing["resource_id"]!=resource_id:
            raise ValueError("Notification identity conflict")
        return "duplicate"
