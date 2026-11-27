"""Account API. Mount only after email verification and rate limits are ready."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, StrictBool
from accounts_rate_limits import allow_attempt
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

    def throttle(policy, identifier):
        if not allow_attempt(policy, identifier):
            raise HTTPException(429, "Too many requests", headers={"Retry-After":str(3600 if policy=="register_ip" else 900)})

    def client_key(request):
        return request.client.host if request.client else "unknown"

    @router.post("/register", status_code=202)
    def register(body: Credentials, request: Request):
        throttle("register_ip", client_key(request))
        try:
            store.register(body.email, body.password)
        except ValueError:
            raise HTTPException(422, "Invalid credentials")
        return {"status":"verification_required"}

    @router.post("/login")
    def login(body: Credentials, request: Request):
        throttle("login_ip", client_key(request))
        throttle("login_email", body.email)
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

    @router.get("/me")
    def me(account_id=Depends(identity)):
        try:
            return ent.account_status(account_id)
        except PermissionError:
            raise HTTPException(403,"Account unavailable")

    class CheckoutConsent(BaseModel):
        consent: StrictBool

    @router.post("/me/checkout")
    def checkout(body: CheckoutConsent, account_id=Depends(identity)):
        import os
        from accounts_checkout import start_checkout
        if os.environ.get("ESTOA_MP_MODE") != "sandbox" or os.environ.get("ESTOA_CHECKOUT_PREVIEW") != "true":
            raise HTTPException(503,"Checkout unavailable")
        try:
            return start_checkout(account_id,body.consent)
        except PermissionError:
            raise HTTPException(409,"Checkout unavailable or consent required")
        except Exception:
            raise HTTPException(503,"Checkout requires reconciliation")

    class TermsConsent(BaseModel):
        version: str = Field(min_length=1,max_length=100)
        consent: StrictBool

    @router.post("/me/terms")
    def terms(body: TermsConsent, account_id=Depends(identity)):
        import os
        from accounts_terms import accept_terms
        if os.environ.get("ESTOA_TERMS_PREVIEW")!="true":
            raise HTTPException(503,"Terms acceptance unavailable")
        try:
            return {"version":body.version,"accepted_at":accept_terms(account_id,body.version,body.consent)}
        except ValueError:
            raise HTTPException(409,"Current published terms and explicit consent required")
        except PermissionError:
            raise HTTPException(403,"Account unavailable")

    return router
