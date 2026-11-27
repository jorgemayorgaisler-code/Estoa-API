BEGIN;
CREATE INDEX IF NOT EXISTS account_sessions_expiry_idx ON account_sessions(expires_at);
CREATE INDEX IF NOT EXISTS email_verification_expiry_idx ON email_verification_tokens(expires_at);
CREATE INDEX IF NOT EXISTS password_reset_expiry_idx ON password_reset_tokens(expires_at);
CREATE INDEX IF NOT EXISTS auth_rate_limits_window_idx ON auth_rate_limits(window_start);
COMMIT;
