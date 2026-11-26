"""Internal verification primitives. Delivery and rate limiting required before exposure."""
import secrets
from accounts_security import session_digest
from accounts_store import connection

def issue_verification(account_id):
    token=secrets.token_urlsafe(32)
    with connection() as conn:
        row=conn.execute("SELECT id FROM accounts WHERE id=%s AND email_verified_at IS NULL AND disabled_at IS NULL FOR UPDATE",(account_id,)).fetchone()
        if not row:
            return None
        conn.execute("UPDATE email_verification_tokens SET consumed_at=now() WHERE account_id=%s AND consumed_at IS NULL",(account_id,))
        conn.execute("INSERT INTO email_verification_tokens(token_hash,account_id,expires_at) VALUES (%s,%s,now()+interval '30 minutes')",(session_digest(token),account_id))
    return token

def consume_verification(token):
    if not isinstance(token,str) or len(token)!=43 or not token.isascii():
        return False
    with connection() as conn:
        digest=session_digest(token)
        candidate=conn.execute("SELECT account_id FROM email_verification_tokens WHERE token_hash=%s",(digest,)).fetchone()
        if not candidate:
            return False
        account=conn.execute("SELECT id FROM accounts WHERE id=%s AND disabled_at IS NULL FOR UPDATE",(candidate["account_id"],)).fetchone()
        if not account:
            return False
        row=conn.execute("UPDATE email_verification_tokens SET consumed_at=now() WHERE token_hash=%s AND consumed_at IS NULL AND expires_at>now() RETURNING account_id",(digest,)).fetchone()
        if not row:
            return False
        conn.execute("UPDATE accounts SET email_verified_at=COALESCE(email_verified_at,now()) WHERE id=%s",(row["account_id"],))
        return True
