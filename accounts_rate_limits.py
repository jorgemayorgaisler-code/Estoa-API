"""Fixed-window throttling shared across application workers."""
import hashlib
import hmac
import os
from accounts_store import connection

POLICIES = {"login_ip": (50, 900), "login_email": (8, 900),
            "register_ip": (10, 3600), "reset_ip": (10, 3600),
            "reset_email": (3, 3600), "verify_ip": (30, 900)}

def allow_attempt(policy, identifier):
    limit, seconds = POLICIES[policy]
    secret = os.environ.get("ESTOA_RATE_LIMIT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("Rate limiting secret not configured")
    key = hmac.new(secret.encode(), (policy + ":" + identifier.strip().lower()).encode(), hashlib.sha256).digest()
    with connection() as conn:
        row = conn.execute("""INSERT INTO auth_rate_limits(bucket_key,window_start,attempts)
            VALUES (%s,to_timestamp(floor(extract(epoch from now()) / %s) * %s),1)
            ON CONFLICT (bucket_key,window_start) DO UPDATE
            SET attempts=LEAST(auth_rate_limits.attempts+1,%s)
            RETURNING attempts""",(key,seconds,seconds,limit+1)).fetchone()
        return row["attempts"] <= limit

def prune_expired_buckets():
    with connection() as conn:
        return conn.execute("DELETE FROM auth_rate_limits WHERE window_start < now()-interval '2 hours'").rowcount
