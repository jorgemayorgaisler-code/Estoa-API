"""Signature verification only; provider contract must be verified before exposure."""
import hashlib
import hmac
import os
import re
import time

def verify_signature(data_id, request_id, signature, now=None):
    secret=os.environ.get("ESTOA_MP_WEBHOOK_SECRET","")
    if not secret or not data_id or not request_id or not signature:
        return False
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}",data_id) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}",request_id):
        return False
    parts={}
    for item in signature.split(","):
        key,sep,value=item.strip().partition("=")
        if not sep or key in parts:
            return False
        parts[key]=value
    ts=parts.get("ts","")
    digest=parts.get("v1","")
    if not re.fullmatch(r"[0-9]{10,13}",ts) or not re.fullmatch(r"[0-9a-fA-F]{64}",digest):
        return False
    timestamp=int(ts)
    if len(ts)==13:
        timestamp/=1000
    if abs((time.time() if now is None else now)-timestamp)>300:
        return False
    manifest=f"id:{data_id.lower()};request-id:{request_id};ts:{ts};"
    expected=hmac.new(secret.encode(),manifest.encode(),hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected,digest.lower())
