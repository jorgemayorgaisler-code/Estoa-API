"""Station entitlement operations; account ID must come from a validated session."""
from accounts_store import connection

def select_free_station(account_id, station_id, valid_station_ids):
    if station_id not in valid_station_ids:
        raise ValueError("Unknown station")
    with connection() as conn:
        account=conn.execute("SELECT id FROM accounts WHERE id=%s AND disabled_at IS NULL AND email_verified_at IS NOT NULL FOR UPDATE",(account_id,)).fetchone()
        if not account:
            raise PermissionError("Account unavailable")
        conn.execute("INSERT INTO free_station_entitlements (account_id,station_id) VALUES (%s,%s) ON CONFLICT (account_id) DO NOTHING",(account_id,station_id))
        row=conn.execute("SELECT station_id FROM free_station_entitlements WHERE account_id=%s",(account_id,)).fetchone()
        if row["station_id"] != station_id:
            raise PermissionError("Free station already selected")
        return row["station_id"]

def allowed_stations(account_id, valid_station_ids):
    valid=set(valid_station_ids)
    with connection() as conn:
        row=conn.execute("""SELECT a.id, f.station_id,
            EXISTS (SELECT 1 FROM subscriptions s WHERE s.account_id=a.id
            AND s.status='authorized' AND s.access_until>now()) AS premium
            FROM accounts a LEFT JOIN free_station_entitlements f ON f.account_id=a.id
            WHERE a.id=%s AND a.disabled_at IS NULL AND a.email_verified_at IS NOT NULL""",(account_id,)).fetchone()
    if not row:
        return set()
    return valid if row["premium"] else ({row["station_id"]} & valid)

def require_station(account_id, station_id, valid_station_ids):
    if station_id not in allowed_stations(account_id,valid_station_ids):
        raise PermissionError("Station not included in account")
