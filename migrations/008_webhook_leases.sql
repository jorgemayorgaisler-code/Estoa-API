BEGIN;
ALTER TABLE payment_webhook_inbox ADD COLUMN IF NOT EXISTS next_attempt_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE payment_webhook_inbox ADD COLUMN IF NOT EXISTS lease_until timestamptz;
ALTER TABLE payment_webhook_inbox ADD COLUMN IF NOT EXISTS lease_token uuid;
CREATE INDEX IF NOT EXISTS webhook_inbox_ready_idx ON payment_webhook_inbox(state,next_attempt_at);
COMMIT;
