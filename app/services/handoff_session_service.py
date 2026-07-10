from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import HandoffSession, utc_now


def get_active_handoff(db: Session, user_id: str | None) -> HandoffSession | None:
    if not user_id:
        return None

    now = utc_now()
    return (
        db.query(HandoffSession)
        .filter(
            HandoffSession.user_id == user_id,
            HandoffSession.active.is_(True),
            HandoffSession.expires_at > now,
        )
        .first()
    )


def activate_handoff(db: Session, user_id: str | None, reason: str) -> HandoffSession | None:
    if not user_id:
        return None

    now = utc_now()
    expires_at = now + timedelta(hours=max(settings.handoff_pause_hours, 1))
    handoff = db.query(HandoffSession).filter(HandoffSession.user_id == user_id).first()
    if handoff:
        handoff.active = True
        handoff.reason = reason
        handoff.started_at = now
        handoff.expires_at = expires_at
        handoff.resolved_at = None
    else:
        handoff = HandoffSession(
            user_id=user_id,
            active=True,
            reason=reason,
            started_at=now,
            expires_at=expires_at,
        )
        db.add(handoff)
    return handoff
