"""Opt-in email verification and reset endpoints."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from accounts_store import connection
from accounts_verification import issue_verification, consume_verification
from accounts_reset import issue_reset, consume_reset
from accounts_rate_limits import allow_attempt
from accounts_mail import send_code

class Email(BaseModel):
    email: str=Field(min_length=3,max_length=254)
class Code(BaseModel):
    token: str=Field(min_length=43,max_length=43)
class Reset(Code):
    password: str=Field(min_length=12,max_length=128)

def build_email_router():
    router=APIRouter(prefix="/accounts")
    def limit(policy,key):
        if not allow_attempt(policy,key):
            raise HTTPException(429,"Too many requests")
    def ip(request):
        return request.client.host if request.client else "unknown"
    @router.post("/verification/request",status_code=202)
    def request_verification(body:Email,request:Request):
        email=body.email.strip().lower()
        limit("reset_ip",ip(request))
        limit("reset_email",email)
        with connection() as conn:
            row=conn.execute("SELECT id FROM accounts WHERE email=%s AND email_verified_at IS NULL AND disabled_at IS NULL",(email,)).fetchone()
        if row:
            token=issue_verification(row["id"])
            if token:
                try: send_code(email,token,"verify")
                except Exception: pass
        return {"status":"accepted"}
    @router.post("/verification/confirm")
    def confirm(body:Code,request:Request):
        limit("verify_ip",ip(request))
        if not consume_verification(body.token):
            raise HTTPException(400,"Invalid or expired code")
        return {"status":"verified"}
    @router.post("/reset/request",status_code=202)
    def request_reset(body:Email,request:Request):
        email=body.email.strip().lower()
        limit("reset_ip",ip(request))
        limit("reset_email",email)
        token=issue_reset(email)
        if token:
            try: send_code(email,token,"reset")
            except Exception: pass
        return {"status":"accepted"}
    @router.post("/reset/confirm")
    def reset(body:Reset,request:Request):
        limit("verify_ip",ip(request))
        if not consume_reset(body.token,body.password):
            raise HTTPException(400,"Invalid or expired code")
        return {"status":"reset"}
    return router
