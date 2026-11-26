import uuid
from accounts_store import connection

MAX_ATTEMPTS=5

def claim():
    token=uuid.uuid4()
    with connection() as conn:
        conn.execute("""UPDATE payment_webhook_inbox SET state='review',lease_token=NULL,lease_until=NULL
            WHERE state='processing' AND lease_until<=now() AND attempts>=%s""",(MAX_ATTEMPTS,))
        return conn.execute("""WITH candidate AS (
            SELECT request_id FROM payment_webhook_inbox
            WHERE attempts<%s AND ((state='pending' AND next_attempt_at<=now())
              OR (state='processing' AND lease_until<=now()))
            ORDER BY received_at,request_id FOR UPDATE SKIP LOCKED LIMIT 1
        ) UPDATE payment_webhook_inbox i SET state='processing',attempts=i.attempts+1,
            lease_token=%s,lease_until=now()+interval '2 minutes'
            FROM candidate c WHERE i.request_id=c.request_id
            RETURNING i.request_id,i.resource_id,i.lease_token,i.attempts""",(MAX_ATTEMPTS,token)).fetchone()

def finish(request_id,token,success):
    with connection() as conn:
        row=conn.execute("""UPDATE payment_webhook_inbox SET
            state=CASE WHEN %s THEN 'processed' WHEN attempts>=%s THEN 'review' ELSE 'pending' END,
            next_attempt_at=now()+interval '1 minute'*attempts,
            lease_token=NULL,lease_until=NULL
            WHERE request_id=%s AND lease_token=%s AND state='processing' AND lease_until>now()
            RETURNING state""",(success,MAX_ATTEMPTS,request_id,token)).fetchone()
        return row["state"] if row else None

# No provider dispatcher or automatic worker is enabled yet.
