BEGIN;
CREATE TABLE IF NOT EXISTS email_verification_tokens (
 token_hash bytea PRIMARY KEY,
 account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
 expires_at timestamptz NOT NULL,
 consumed_at timestamptz
);
CREATE INDEX IF NOT EXISTS email_verification_account_idx ON email_verification_tokens(account_id);
COMMIT;
