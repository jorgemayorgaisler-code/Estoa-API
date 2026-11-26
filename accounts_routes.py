"""Account API. Mount only after email verification and rate limits are ready."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import accounts_store as store
import accounts_entitlements as ent

def build_router(valid_station_ids):
    router = APIRouter(prefix="/accounts", tags=["accounts"])
    bearer = HTTPBearer(auto_error=False)
    stations = frozenset(valid_station_ids)

    class Credentials(BaseModel):
        email: str = Field(min_length=3, max_length=254)
        password: str = Field(min_length=12, max_length=128)

    class StationChoice(BaseModel):
        station_id: str = Field(min_length=6, max_length=6)

    def identity(auth: HTTPAuthorizationCredentials = Depends(bearer)):
        account_id = store.session_account(auth.credentials) if auth else None
        if account_id is None:
            raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate":"Bearer"})
        return account_id

    @router.post("/register", status_code=202)
    def register(body: Credentials):
        try:
            store.register(body.email, body.password)
        except ValueError:
            raise HTTPException(422, "Invalid credentials")
        return {"status":"verification_required"}

    @router.post("/login")
    def login(body: Credentials):
        result = store.login(body.email, body.password)
        if not result:
            raise HTTPException(401, "Invalid credentials or account unavailable")
        token, expiry = result
        return {"access_token":token,"token_type":"bearer","expires_at":expiry}

    @router.post("/logout", status_code=204)
    def logout(auth: HTTPAuthorizationCredentials = Depends(bearer)):
        if auth:
            store.logout(auth.credentials)

    @router.get("/me/stations")
    def my_stations(account_id=Depends(identity)):
        return {"station_ids":sorted(ent.allowed_stations(account_id, stations))}

    @router.post("/me/free-station")
    def choose(body: StationChoice, account_id=Depends(identity)):
        try:
            return {"station_id":ent.select_free_station(account_id,body.station_id,stations)}
        except ValueError:
            raise HTTPException(404,"Unknown station")
        except PermissionError:
            raise HTTPException(409,"Station selection unavailable")

    @router.post("/me/trial")
    def trial(account_id=Depends(identity)):
        try:
            return ent.activate_trial(account_id)
        except PermissionError:
            raise HTTPException(403,"Account unavailable")

    return router
