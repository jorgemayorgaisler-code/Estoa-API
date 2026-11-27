BEGIN;
CREATE TABLE IF NOT EXISTS account_admin_grants (
 account_id uuid PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
 granted_at timestamptz NOT NULL DEFAULT now(),
 revoked_at timestamptz
);
COMMIT;
