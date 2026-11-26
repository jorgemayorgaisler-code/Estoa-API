BEGIN;
CREATE TABLE IF NOT EXISTS admin_access_audit (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 account_id uuid REFERENCES accounts(id) ON DELETE SET NULL,
 action text NOT NULL CHECK(action IN ('summary_read')),
 occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS admin_access_audit_time_idx ON admin_access_audit(occurred_at);
COMMIT;
