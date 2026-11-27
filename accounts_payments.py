"""Internal Mercado Pago client. Not exposed or enabled in production."""
import json
import os
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.parse import quote

LAUNCH_PRICE_CLP = 990
BASE = "https://api.mercadopago.com"

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url,code,"Provider redirect rejected",headers,fp)

def provider_request(path, payload=None):
    token=os.environ.get("ESTOA_MP_TEST_ACCESS_TOKEN","")
    if os.environ.get("ESTOA_MP_MODE")!="sandbox" or not token.startswith("TEST-"):
        raise RuntimeError("Sandbox credentials required")
    req=Request(BASE+path, data=json.dumps(payload).encode() if payload is not None else None,
                headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},
                method="POST" if payload is not None else "GET")
    with build_opener(NoRedirect()).open(req,timeout=15) as response:
        raw=response.read(1048577)
        if len(raw)>1048576:
            raise ValueError("Provider response too large")
        result=json.loads(raw)
        if not isinstance(result,dict):
            raise ValueError("Invalid provider response")
        return result

def create_pending_subscription(account_id, verified_email):
    """Caller must verify eligibility, consent and prevent duplicate creation."""
    back_url=os.environ.get("ESTOA_MP_BACK_URL","")
    parsed=urlsplit(back_url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise RuntimeError("HTTPS return URL required")
    return provider_request("/preapproval", {
        "reason":"ESTOA Premium",
        "external_reference":str(account_id),
        "payer_email":verified_email,
        "auto_recurring":{"frequency":1,"frequency_type":"months","transaction_amount":LAUNCH_PRICE_CLP,"currency_id":"CLP"},
        "back_url":back_url,
        "status":"pending"
    })

def fetch_subscription(provider_id):
    return provider_request("/preapproval/"+quote(provider_id,safe=""))

def fetch_authorized_payment(resource_id):
    return provider_request("/authorized_payments/"+quote(str(resource_id),safe=""))

def fetch_payment(resource_id):
    return provider_request("/v1/payments/"+quote(str(resource_id),safe=""))
