BEGIN;
CREATE TABLE IF NOT EXISTS password_reset_tokens (
 token_hash bytea PRIMARY KEY,
 account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
 expires_at timestamptz NOT NULL,
 consumed_at timestamptz
);
CREATE INDEX IF NOT EXISTS password_reset_account_idx ON password_reset_tokens(account_id);
COMMIT;
