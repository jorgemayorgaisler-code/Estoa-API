# Operations
Run auth maintenance manually in isolated preview before scheduling. Proposed retention: expired authentication records seven days, rate buckets two hours. Confirm retention policy before production. Never prune payment ledger through this job.
Aggregate counters: verified accounts, active sessions, pending and review notifications. No public admin endpoint. Do not log passwords, bearer tokens, reset codes or payment payloads.
Multiple sessions are currently permitted; logout revokes current session and password reset revokes all. No device limit has been approved.
Mobile acceptance: iPhone Safari/PWA, Android Chrome, login/logout, expired session, station selection, trial expiry, offline/no public fallback, keyboard and small viewport. Physical-device checks remain pending.
