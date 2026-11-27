"""Run only against an isolated preview database after backup."""
import os
from pathlib import Path
from hashlib import sha256
from accounts_store import connection

def migrate():
    if os.environ.get("ESTOA_MIGRATION_PREVIEW")!="true":
        raise RuntimeError("Preview migration disabled")
    files=sorted(Path(__file__).resolve().parent.joinpath("migrations").glob("[0-9][0-9][0-9]_*.sql"))
    with connection() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(78123901)")
        conn.execute("CREATE TABLE IF NOT EXISTS estoa_schema_history (name text PRIMARY KEY, digest text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())")
        for path in files:
            raw=path.read_bytes()
            digest=sha256(raw).hexdigest()
            old=conn.execute("SELECT digest FROM estoa_schema_history WHERE name=%s",(path.name,)).fetchone()
            if old:
                if old["digest"]!=digest:
                    raise RuntimeError("Migration checksum mismatch: "+path.name)
                continue
            sql=raw.decode().strip()
            if sql.startswith("BEGIN;") and sql.endswith("COMMIT;"):
                sql=sql[len("BEGIN;"):-len("COMMIT;")]
            else:
                raise RuntimeError("Expected transaction wrapper: "+path.name)
            conn.execute(sql)
            conn.execute("INSERT INTO estoa_schema_history(name,digest) VALUES (%s,%s)",(path.name,digest))
    return len(files)

if __name__=="__main__":
    print("Migration files verified:",migrate())
