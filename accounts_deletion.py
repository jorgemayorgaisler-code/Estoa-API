import uuid
from accounts_store import connection
from accounts_security import verify_password

def request_deletion(account_id,password):
    if not isinstance(password,str) or not 12<=len(password)<=128:
        raise ValueError("Reauthentication required")
    request_id=uuid.uuid4()
    with connection() as conn:
        row=conn.execute("SELECT password_hash,disabled_at,email_verified_at FROM accounts WHERE id=%s FOR UPDATE",(account_id,)).fetchone()
        if not row or row["disabled_at"] or not row["email_verified_at"] or not verify_password(password,row["password_hash"]):
            raise PermissionError("Reauthentication failed")
        existing=conn.execute("SELECT id,status FROM account_deletion_requests WHERE account_id=%s AND status IN ('pending_review','billing_review')",(account_id,)).fetchone()
        if existing:
            return {"request_id":str(existing["id"]),"status":existing["status"]}
        subscriptions=conn.execute("SELECT count(*) AS n FROM subscriptions WHERE account_id=%s AND status IN ('pending','authorized','paused')",(account_id,)).fetchone()["n"]
        status="billing_review" if subscriptions else "pending_review"
        conn.execute("INSERT INTO account_deletion_requests(id,account_id,status) VALUES (%s,%s,%s)",(request_id,account_id,status))
        return {"request_id":str(request_id),"status":status}
