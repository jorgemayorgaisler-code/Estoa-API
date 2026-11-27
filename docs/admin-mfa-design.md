# Administrative step-up authentication
Keep admin routes unmounted until implemented and tested.
Prefer WebAuthn/passkeys with verified origin and RP ID, or vetted TOTP implementation with encrypted secrets and replay protection. No custom cryptography.
Require existing verified account, explicit revocable grant, fresh second-factor verification bound to session, maximum step-up lifetime 10 minutes (provisional), rate limits and audit.
Enrollment and recovery require separate identity verification. Never log secrets or recovery codes. Revocation and password reset invalidate elevated sessions. No self-grant.
Test missing factor, replay, expired challenge, wrong origin, concurrent use, revoked grant, disabled account, reset and recovery. Choose implementation before adding dependencies.
