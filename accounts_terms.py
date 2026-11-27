import os
from accounts_store import connection

def accept_terms(account_id,version,consent):
    current=os.environ.get("ESTOA_TERMS_VERSION")
    if consent is not True or not current or version!=current:
        raise ValueError("Explicit acceptance of current terms required")
    with connection() as conn:
        account=conn.execute("SELECT id FROM accounts WHERE id=%s AND email_verified_at IS NOT NULL AND disabled_at IS NULL FOR UPDATE",(account_id,)).fetchone()
        if not account:
            raise PermissionError("Account unavailable")
        doc=conn.execute("SELECT version FROM contractual_documents WHERE version=%s AND published_at<=now()",(version,)).fetchone()
        if not doc:
            raise ValueError("Terms not published")
        conn.execute("INSERT INTO contractual_acceptances(account_id,document_version) VALUES (%s,%s) ON CONFLICT DO NOTHING",(account_id,version))
        return conn.execute("SELECT accepted_at FROM contractual_acceptances WHERE account_id=%s AND document_version=%s",(account_id,version)).fetchone()["accepted_at"]

def terms_status(account_id):
    version=os.environ.get("ESTOA_TERMS_VERSION")
    if not version:
        raise ValueError("Terms unavailable")
    with connection() as conn:
        row=conn.execute("""SELECT d.version,d.content_sha256,d.published_at,a.accepted_at
            FROM contractual_documents d
            LEFT JOIN contractual_acceptances a ON a.document_version=d.version AND a.account_id=%s
            WHERE d.version=%s AND d.published_at<=now()""",(account_id,version)).fetchone()
        if not row:
            raise ValueError("Terms unavailable")
        return dict(row)
