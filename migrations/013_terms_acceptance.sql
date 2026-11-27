BEGIN;
CREATE TABLE contractual_documents (
    version text PRIMARY KEY,
    content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    published_at timestamptz NOT NULL
);
CREATE TABLE contractual_acceptances (
    account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    document_version text NOT NULL REFERENCES contractual_documents(version),
    accepted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(account_id,document_version)
);
COMMIT;
