"""Private navigation preview; public integration API remains unchanged."""
from fastapi import APIRouter, Depends
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
    return router
