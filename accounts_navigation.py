"""Private navigation preview; public integration API remains unchanged."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from accounts_store import session_account
from accounts_entitlements import allowed_stations
from accounts_station_guard import build_station_guard

ROUTES = ("/tide-curve","/current-curve","/sun-events","/current/diagnostic",
          "/conditions/at","/conditions/now","/forecast","/weak-windows",
          "/capabilities","/tide-events")

def build_navigation_router(source_app, valid_station_ids):
    router=APIRouter(prefix="/private",tags=["private-navigation"])
    guard=build_station_guard(valid_station_ids)
    for path in ROUTES:
        matches=[r for r in source_app.routes if getattr(r,"path",None)==path and "GET" in (getattr(r,"methods",None) or ())]
        if len(matches)!=1:
            raise RuntimeError("Missing or ambiguous navigation route: "+path)
        router.add_api_route(path,matches[0].endpoint,methods=["GET"],
                             dependencies=[Depends(guard)])
    map_routes=[r for r in source_app.routes if getattr(r,"path",None)=="/conditions/map" and "GET" in (getattr(r,"methods",None) or ())]
    if len(map_routes)!=1:
        raise RuntimeError("Missing map route")
    map_handler=map_routes[0].endpoint
    bearer=HTTPBearer(auto_error=False)
    valid=frozenset(valid_station_ids)
    @router.get("/conditions/map")
    def private_map(at_utc: datetime | None=None, auth: HTTPAuthorizationCredentials=Depends(bearer)):
        account_id=session_account(auth.credentials) if auth else None
        if account_id is None:
            raise HTTPException(401,"Authentication required")
        allowed=allowed_stations(account_id,valid)
        result=map_handler(at_utc)
        return {"at_utc":result["at_utc"],"stations":[s for s in result["stations"] if s["station_id"] in allowed]}
    return router
