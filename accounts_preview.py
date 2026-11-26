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
