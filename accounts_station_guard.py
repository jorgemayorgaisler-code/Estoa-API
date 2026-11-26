"""Dependency factory for future private station-scoped routes."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from accounts_store import session_account
from accounts_entitlements import require_station

def build_station_guard(valid_station_ids):
    valid=frozenset(valid_station_ids)
    bearer=HTTPBearer(auto_error=False)
    def guard(station_id: str, auth: HTTPAuthorizationCredentials=Depends(bearer)):
        account_id=session_account(auth.credentials) if auth else None
        if account_id is None:
            raise HTTPException(401,"Authentication required")
        if station_id not in valid:
            raise HTTPException(404,"Unknown station")
        try:
            require_station(account_id,station_id,valid)
        except PermissionError:
            raise HTTPException(403,"Station not included in plan")
        return account_id
    return guard
