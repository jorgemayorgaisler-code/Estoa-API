BEGIN;
CREATE TABLE IF NOT EXISTS accounts (
 id uuid PRIMARY KEY,
 email text NOT NULL UNIQUE CHECK (email = lower(btrim(email))),
 password_hash text NOT NULL,
 email_verified_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 disabled_at timestamptz
);
CREATE TABLE IF NOT EXISTS free_station_entitlements (
 account_id uuid PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
 station_id text NOT NULL CHECK (station_id ~ '^CUR[0-9]{3}$'),
 selected_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS account_sessions (
 token_hash bytea PRIMARY KEY,
 account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 revoked_at timestamptz,
 CHECK (expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS account_sessions_account_idx ON account_sessions(account_id);
CREATE TABLE IF NOT EXISTS subscriptions (
 provider_id text PRIMARY KEY,
 account_id uuid NOT NULL REFERENCES accounts(id),
 status text NOT NULL CHECK (status IN ('pending','authorized','paused','cancelled','expired')),
 amount_clp integer NOT NULL CHECK (amount_clp > 0),
 access_until timestamptz,
 verified_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS subscriptions_account_idx ON subscriptions(account_id);
CREATE TABLE IF NOT EXISTS payment_webhook_events (
 provider_event_id text PRIMARY KEY,
 processed_at timestamptz NOT NULL DEFAULT now()
);
COMMIT;
