import hashlib
import hmac
import os
import re

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


def verify_signature(secret, signature, request_id, data_id):
    if not all((secret, signature, request_id, data_id)):
        return False
    fields = dict(part.strip().split('=', 1) for part in signature.split(',') if '=' in part)
    ts = fields.get('ts', '')
    digest = fields.get('v1', '')
    if not ts.isdigit() or not re.fullmatch(r'[a-fA-F0-9]{64}', digest):
        return False
    manifest = f'id:{data_id.lower()};request-id:{request_id};ts:{ts};'
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, digest.lower())


@router.post('/webhooks/mercadopago')
async def webhook(request: Request):
    secret = os.getenv('MERCADOPAGO_WEBHOOK_SECRET')
    if not secret:
        raise HTTPException(503, 'Webhook is not configured')
    data_id = request.query_params.get('data.id', '')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', data_id):
        raise HTTPException(400, 'Invalid notification identifier')
    if not verify_signature(secret, request.headers.get('x-signature', ''), request.headers.get('x-request-id', ''), data_id):
        raise HTTPException(401, 'Invalid signature')
    return {'received': True, 'premium_activated': False}
