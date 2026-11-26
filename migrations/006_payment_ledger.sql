BEGIN;
CREATE TABLE IF NOT EXISTS subscription_payments (
 provider_payment_id text PRIMARY KEY,
 provider_id text NOT NULL REFERENCES subscriptions(provider_id),
 amount_clp integer NOT NULL CHECK (amount_clp > 0),
 currency text NOT NULL CHECK (currency = 'CLP'),
 period_start timestamptz NOT NULL,
 period_end timestamptz NOT NULL,
 status text NOT NULL CHECK (status IN ('approved','refunded','charged_back')),
 verified_at timestamptz NOT NULL DEFAULT now(),
 CHECK (period_end > period_start),
 UNIQUE(provider_id,period_start)
);
CREATE TABLE IF NOT EXISTS checkout_reservations (
 account_id uuid PRIMARY KEY REFERENCES accounts(id),
 request_id uuid NOT NULL UNIQUE,
 created_at timestamptz NOT NULL DEFAULT now(),
 provider_id text UNIQUE REFERENCES subscriptions(provider_id),
 status text NOT NULL CHECK (status IN ('reserved','bound','review_required'))
);
COMMIT;
