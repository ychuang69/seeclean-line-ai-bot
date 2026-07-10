import json
from uuid import uuid4
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MessageLog
from app.services.handoff_service import needs_handoff
from app.services.handoff_session_service import activate_handoff, get_active_handoff
from app.services.intent_service import Intent, detect_intent
from app.services.reply_service import build_reply


def process_text_message(
    db: Session,
    *,
    user_id: str | None,
    text: str,
    source: str = "test",
    dedupe_key: str | None = None,
    message_id: str | None = None,
    event_id: str | None = None,
    event_type: str | None = None,
    raw_event: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = dedupe_key or event_id or message_id
    if key:
        existing = db.query(MessageLog).filter(MessageLog.dedupe_key == key).first()
        if existing:
            return {
                "deduplicated": True,
                "intent": existing.intent,
                "reply": existing.reply_text,
                "log_id": existing.id,
            }
    else:
        key = f"{source}:{uuid4()}"

    active_handoff = get_active_handoff(db, user_id) if source == "line" else None
    if active_handoff:
        intent = Intent.HANDOFF
        reply = None
        should_reply = False
    else:
        intent = detect_intent(text, is_handoff=needs_handoff(text))
        reply = build_reply(intent, text)
        should_reply = True
        if source == "line" and intent == Intent.HANDOFF:
            activate_handoff(db, user_id, text)

    log = MessageLog(
        dedupe_key=key,
        source=source,
        user_id=user_id,
        message_id=message_id,
        event_id=event_id,
        event_type=event_type,
        intent=str(intent),
        user_text=text,
        reply_text=reply,
        raw_event=json.dumps(raw_event or {}, ensure_ascii=False),
    )
    db.add(log)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(MessageLog).filter(MessageLog.dedupe_key == key).first()
        return {
            "deduplicated": True,
            "intent": existing.intent if existing else str(intent),
            "reply": existing.reply_text if existing else reply,
            "log_id": existing.id if existing else None,
            "should_reply": False,
            "handoff_active": bool(active_handoff),
        }
    db.refresh(log)

    return {
        "deduplicated": False,
        "intent": str(intent),
        "reply": reply,
        "log_id": log.id,
        "should_reply": should_reply,
        "handoff_active": bool(active_handoff or intent == Intent.HANDOFF),
    }
