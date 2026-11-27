BEGIN;
CREATE TABLE IF NOT EXISTS premium_trials (
 account_id uuid PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
 activated_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL,
 CHECK (expires_at > activated_at)
);
COMMIT;
