"""Isolated preview entrypoint: uvicorn accounts_preview:app.
Never deploy alongside public production credentials.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from accounts_store import session_account
from accounts_entitlements import allowed_stations
from app import stations
from app import app as source_app, REG
from accounts_routes import build_router
from accounts_navigation import build_navigation_router

app=FastAPI(title="ESTOA private preview")
valid=frozenset(str(x) for x in REG.station_id)
app.include_router(build_router(valid))
app.include_router(build_navigation_router(source_app,valid))

@app.get("/health")
def health():
    return {"status":"ok","service":"ESTOA private preview"}

bearer=HTTPBearer(auto_error=False)

@app.get("/private/stations")
def private_stations(auth: HTTPAuthorizationCredentials=Depends(bearer)):
    account_id=session_account(auth.credentials) if auth else None
    if account_id is None:
        raise HTTPException(401,"Authentication required")
    allowed=allowed_stations(account_id,valid)
    return [dict(s, included=s["station_id"] in allowed) for s in stations()]

import os
from urllib.parse import urlsplit
from fastapi.middleware.cors import CORSMiddleware
origin=os.environ.get("ESTOA_PREVIEW_ORIGIN","")
if origin:
    parsed=urlsplit(origin)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment or "*" in origin:
        raise RuntimeError("Invalid preview origin")
    app.add_middleware(CORSMiddleware,allow_origins=[origin],allow_methods=["GET","POST"],allow_headers=["Authorization","Content-Type"],allow_credentials=False)

@app.middleware("http")
async def no_private_cache(request,call_next):
    response=await call_next(request)
    if request.url.path.startswith(("/private/","/accounts/","/admin/","/payments/")):
        response.headers["Cache-Control"]="no-store"
        response.headers["Pragma"]="no-cache"
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="no-referrer"
    return response

if os.environ.get("ESTOA_EMAIL_PREVIEW")=="true":
    from accounts_email_routes import build_email_router
    app.include_router(build_email_router())

if os.environ.get("ESTOA_WEBHOOK_PREVIEW")=="true" and os.environ.get("ESTOA_MP_MODE")=="sandbox":
    from accounts_webhook_routes import build_webhook_router
    app.include_router(build_webhook_router())
