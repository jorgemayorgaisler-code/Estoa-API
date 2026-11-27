"""Account persistence. Not mounted on the public API."""
import os
import uuid
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from accounts_security import hash_password, verify_password, new_session, session_digest

@contextmanager
def connection():
    dsn = os.environ.get("ESTOA_DATABASE_URL")
    if not dsn:
        raise RuntimeError("Account database is not configured")
    with psycopg.connect(dsn, connect_timeout=5, row_factory=dict_row) as conn:
        yield conn

def register(email, password):
    email = email.strip().lower()
    if len(email) > 254 or email.count("@") != 1 or any(c.isspace() for c in email) or not all(email.split("@")):
        raise ValueError("Invalid email")
    encoded = hash_password(password)
    account_id = uuid.uuid4()
    with connection() as conn:
        row = conn.execute(
            "INSERT INTO accounts (id,email,password_hash) VALUES (%s,%s,%s) ON CONFLICT (email) DO NOTHING RETURNING id",
            (account_id,email,encoded)).fetchone()
    return row["id"] if row else None

_DUMMY_HASH = hash_password(uuid.uuid4().hex)

def login(email, password):
    with connection() as conn:
        row = conn.execute("SELECT id,password_hash,email_verified_at,disabled_at FROM accounts WHERE email=%s FOR UPDATE",
                           (email.strip().lower(),)).fetchone()
        verified = verify_password(password,row["password_hash"] if row else _DUMMY_HASH)
        if not row or not verified or not row["email_verified_at"] or row["disabled_at"]:
            return None
        token,digest,expires = new_session()
        conn.execute("INSERT INTO account_sessions (token_hash,account_id,expires_at) VALUES (%s,%s,%s)",
                     (digest,row["id"],expires))
        return token,expires

def session_account(token):
    if not isinstance(token,str) or len(token)!=43 or not token.isascii():
        return None
    with connection() as conn:
        row=conn.execute("""SELECT a.id FROM account_sessions s JOIN accounts a ON a.id=s.account_id
            WHERE s.token_hash=%s AND s.revoked_at IS NULL AND s.expires_at>now()
            AND a.disabled_at IS NULL AND a.email_verified_at IS NOT NULL""",(session_digest(token),)).fetchone()
        return row["id"] if row else None

def logout(token):
    if not isinstance(token,str) or len(token)!=43 or not token.isascii():
        return
    with connection() as conn:
        conn.execute("UPDATE account_sessions SET revoked_at=now() WHERE token_hash=%s AND revoked_at IS NULL",
                     (session_digest(token),))

def revoke_all_sessions(account_id,password):
    with connection() as conn:
        row=conn.execute("SELECT password_hash,disabled_at,email_verified_at FROM accounts WHERE id=%s FOR UPDATE",(account_id,)).fetchone()
        if not row or row["disabled_at"] or not row["email_verified_at"] or not verify_password(password,row["password_hash"]):
            raise PermissionError("Reauthentication failed")
        return conn.execute("UPDATE account_sessions SET revoked_at=now() WHERE account_id=%s AND revoked_at IS NULL",(account_id,)).rowcount
