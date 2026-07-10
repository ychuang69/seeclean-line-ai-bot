from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db, init_db
from app.line_client import reply_message
from app.security import verify_line_signature
from app.services.handoff_notification_service import notify_handoff
from app.services.intent_service import Intent
from app.services.message_router import process_text_message


app = FastAPI(title="See Clean LINE AI Bot")


class TestMessageRequest(BaseModel):
    user_id: str = Field(..., examples=["test001"])
    text: str = Field(..., examples=["請問冷氣清洗多少錢"])


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/line")
async def line_webhook(
    request: Request,
    x_line_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    body = await request.body()
    if not verify_line_signature(body, x_line_signature):
        raise HTTPException(status_code=401, detail="Invalid LINE signature")

    payload = await request.json()
    results = []
    for event in payload.get("events", []):
        if event.get("type") != "message" or event.get("message", {}).get("type") != "text":
            continue

        message = event["message"]
        source = event.get("source", {})
        result = process_text_message(
            db,
            user_id=source.get("userId"),
            text=message.get("text", ""),
            source="line",
            dedupe_key=event.get("webhookEventId") or message.get("id"),
            message_id=message.get("id"),
            event_id=event.get("webhookEventId"),
            event_type=event.get("type"),
            raw_event=event,
        )

        if not result["deduplicated"] and event.get("replyToken"):
            line_result = reply_message(event["replyToken"], result["reply"])
            result["line_reply"] = line_result
        if not result["deduplicated"] and result["intent"] == str(Intent.HANDOFF):
            result["handoff_notification"] = notify_handoff(source.get("userId"), message.get("text", ""))
        results.append(result)

    return {"ok": True, "results": results}


@app.post("/test/message")
def test_message(payload: TestMessageRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    result = process_text_message(
        db,
        user_id=payload.user_id,
        text=payload.text,
        source="test",
        dedupe_key=None,
    )
    return {
        "user_id": payload.user_id,
        "text": payload.text,
        **result,
    }
