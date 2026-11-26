import os
from fastapi import APIRouter, Request, HTTPException
from accounts_webhook_inbox import receive_notification

def build_webhook_router():
    router=APIRouter()
    @router.post("/payments/webhook",status_code=200)
    def webhook(request: Request):
        if os.environ.get("ESTOA_MP_MODE")!="sandbox" or os.environ.get("ESTOA_WEBHOOK_PREVIEW")!="true":
            raise HTTPException(404)
        ids=request.query_params.getlist("data.id")
        if len(ids)!=1:
            raise HTTPException(400,"Invalid resource identifier")
        try:
            receive_notification(ids[0],request.headers.get("x-request-id"),request.headers.get("x-signature"))
        except PermissionError:
            raise HTTPException(401,"Invalid signature")
        except ValueError:
            raise HTTPException(409,"Notification conflict")
        return {"received":True}
    return router
