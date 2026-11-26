BEGIN;
CREATE TABLE IF NOT EXISTS payment_revocations (
 provider_payment_id text PRIMARY KEY,
 provider_id text NOT NULL REFERENCES subscriptions(provider_id),
 status text NOT NULL CHECK(status IN ('refunded','charged_back')),
 verified_at timestamptz NOT NULL DEFAULT now()
);
COMMIT;
