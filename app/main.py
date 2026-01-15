from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import hmac
import hashlib

from app.storage import init_db, insert_message


app = FastAPI()
init_db()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


class WebhookMessage(BaseModel):
    message_id: str
    from_: str
    to: str
    ts: str
    text: str | None = None


@app.get("/")
def root():
    return {"message": "FastAPI running in GitHub Codespaces"}


@app.get("/health/live")
def live():
    return {"status": "live"}


@app.get("/health/ready")
def ready():
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="WEBHOOK_SECRET not set")
    return {"status": "ready"}


@app.post("/webhook")
def webhook(
    payload: WebhookMessage,
    x_signature: str = Header(None)
):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="secret not set")

    body_bytes = payload.json().encode()
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    if x_signature != expected_signature:
        raise HTTPException(status_code=401, detail="invalid signature")

    inserted = insert_message(
        message_id=payload.message_id,
        from_msisdn=payload.from_,
        to_msisdn=payload.to,
        ts=payload.ts,
        text=payload.text
    )

    # idempotent response
    return {"status": "ok"}

