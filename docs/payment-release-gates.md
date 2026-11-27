# Payment release gates
- Reconcile only subscriptions already bound to a verified account through a consented checkout.
- Authenticate webhook before reconciliation; derive event identity from verified provider data, not arbitrary unsigned body fields.
- Subscription authorization alone does not establish successful payment. Verify the actual recurring payment, amount, currency, account binding, billing period and refund/chargeback status before granting access_until.
- Process duplicate events transactionally. Test retry after rollback and concurrent notifications.
- Current conservative policy: paused, cancelled or expired subscriptions lose paid access immediately; confirm paid-through cancellation policy before release.
- Do not mount payment endpoints or use production credentials until sandbox contract tests, consent, duplicate checkout prevention and cancellation policy are complete.
