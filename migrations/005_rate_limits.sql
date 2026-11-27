BEGIN;
CREATE TABLE IF NOT EXISTS auth_rate_limits (
 bucket_key bytea NOT NULL,
 window_start timestamptz NOT NULL,
 attempts integer NOT NULL CHECK (attempts > 0),
 PRIMARY KEY (bucket_key,window_start)
);
CREATE INDEX IF NOT EXISTS auth_rate_limits_window_idx ON auth_rate_limits(window_start);
COMMIT;
