BEGIN;
CREATE TABLE account_deletion_requests (
 id uuid PRIMARY KEY,
 account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
 status text NOT NULL CHECK(status IN ('pending_review','billing_review','completed','rejected')),
 requested_at timestamptz NOT NULL DEFAULT now(),
 reviewed_at timestamptz,
 CHECK ((status IN ('pending_review','billing_review') AND reviewed_at IS NULL) OR (status IN ('completed','rejected') AND reviewed_at IS NOT NULL))
);
CREATE UNIQUE INDEX account_deletion_one_open_idx ON account_deletion_requests(account_id)
WHERE status IN ('pending_review','billing_review');
COMMIT;
