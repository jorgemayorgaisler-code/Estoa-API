BEGIN;
CREATE TABLE IF NOT EXISTS payment_webhook_inbox (
 request_id text PRIMARY KEY,
 resource_id text NOT NULL,
 received_at timestamptz NOT NULL DEFAULT now(),
 state text NOT NULL DEFAULT 'pending' CHECK (state IN ('pending','processing','processed','review')),
 attempts integer NOT NULL DEFAULT 0 CHECK (attempts>=0)
);
COMMIT;
