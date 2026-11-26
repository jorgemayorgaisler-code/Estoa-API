from pathlib import Path
from hashlib import sha256
from accounts_store import connection

def database_ready():
    files=sorted(Path(__file__).resolve().parent.joinpath("migrations").glob("[0-9][0-9][0-9]_*.sql"))
    if not files:
        return False
    try:
        with connection() as conn:
            conn.execute("SET LOCAL statement_timeout = '3000ms'")
            rows=conn.execute("SELECT name,digest FROM estoa_schema_history").fetchall()
            actual={r["name"]:r["digest"] for r in rows}
            expected={p.name:sha256(p.read_bytes()).hexdigest() for p in files}
            return actual==expected
    except Exception:
        return False
