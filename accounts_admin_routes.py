from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from accounts_store import session_account
from accounts_admin import admin_summary

def build_admin_router():
    router=APIRouter(prefix="/admin")
    bearer=HTTPBearer(auto_error=False)
    @router.get("/summary")
    def summary(auth:HTTPAuthorizationCredentials=Depends(bearer)):
        aid=session_account(auth.credentials) if auth else None
        if not aid:
            raise HTTPException(401,"Authentication required")
        try:
            return admin_summary(aid)
        except PermissionError:
            raise HTTPException(403,"Administrative access required")
    return router
