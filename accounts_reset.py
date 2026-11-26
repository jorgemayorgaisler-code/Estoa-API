"""Internal password reset operations; require throttled email delivery before exposure."""
import secrets
from accounts_security import session_digest, hash_password
from accounts_store import connection

def issue_reset(email):
    token=secrets.token_urlsafe(32)
    with connection() as conn:
        account=conn.execute("SELECT id FROM accounts WHERE email=%s AND email_verified_at IS NOT NULL AND disabled_at IS NULL FOR UPDATE",(email.strip().lower(),)).fetchone()
        if not account:
            return None
        aid=account["id"]
        conn.execute("UPDATE password_reset_tokens SET consumed_at=now() WHERE account_id=%s AND consumed_at IS NULL",(aid,))
        conn.execute("INSERT INTO password_reset_tokens(token_hash,account_id,expires_at) VALUES (%s,%s,now()+interval '30 minutes')",(session_digest(token),aid))
    return token

def consume_reset(token,new_password):
    if not isinstance(token,str) or len(token)!=43 or not token.isascii():
        return False
    digest=session_digest(token)
    encoded=hash_password(new_password)
    with connection() as conn:
        candidate=conn.execute("SELECT account_id FROM password_reset_tokens WHERE token_hash=%s",(digest,)).fetchone()
        if not candidate:
            return False
        aid=candidate["account_id"]
        account=conn.execute("SELECT id FROM accounts WHERE id=%s AND disabled_at IS NULL AND email_verified_at IS NOT NULL FOR UPDATE",(aid,)).fetchone()
        if not account:
            return False
        row=conn.execute("UPDATE password_reset_tokens SET consumed_at=now() WHERE token_hash=%s AND consumed_at IS NULL AND expires_at>now() RETURNING account_id",(digest,)).fetchone()
        if not row:
            return False
        conn.execute("UPDATE accounts SET password_hash=%s WHERE id=%s",(encoded,aid))
        conn.execute("UPDATE account_sessions SET revoked_at=now() WHERE account_id=%s AND revoked_at IS NULL",(aid,))
        conn.execute("UPDATE password_reset_tokens SET consumed_at=now() WHERE account_id=%s AND consumed_at IS NULL",(aid,))
        return True
