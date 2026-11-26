"""Isolated preview entrypoint: uvicorn accounts_preview:app.
Never deploy alongside public production credentials.
"""
from fastapi import FastAPI
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
