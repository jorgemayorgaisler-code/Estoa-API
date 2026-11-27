# Mercado Pago notification contract
Reviewed 2026-11-26:
https://www.mercadopago.cl/developers/es/docs/subscriptions/additional-content/your-integrations/notifications/webhooks
https://www.mercadopago.cl/developers/es/docs/subscriptions/additional-content/your-integrations/notifications/additional-info
https://www.mercadopago.cl/developers/es/docs/checkout-api-orders/optional-notifications

Verify x-signature, x-request-id and query data.id using HMAC SHA256. Require complete signed tuple in ESTOA preview; test actual provider retries against timestamp tolerance.
Handle subscription_preapproval, subscription_authorized_payment and payment separately. Fetch authoritative subscription, invoice (/authorized_payments/{id}) and payment (/v1/payments/{id}) before entitlement changes.
Persist authenticated notifications before acknowledging HTTP 200/201 within 22 seconds. A durable worker must retry failed processing; duplicate notifications must not duplicate subscription or paid period.
Do not infer paid period from receipt time or subscription authorization. Confirm invoice-to-payment linkage, account, currency, amount, merchant, refunded amounts and authoritative billing period using sandbox fixtures. Cancellation and partial-refund policy remains a release gate.
No webhook exposure or real charge until sandbox acceptance and deployment approval.
