from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class MessageLog(Base):
    __tablename__ = "message_logs"
    __table_args__ = (
        UniqueConstraint("dedupe_key", name="uq_message_logs_dedupe_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    dedupe_key = Column(String(255), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="line")
    user_id = Column(String(255), nullable=True, index=True)
    message_id = Column(String(255), nullable=True, index=True)
    event_id = Column(String(255), nullable=True, index=True)
    event_type = Column(String(50), nullable=True)
    intent = Column(String(50), nullable=True)
    user_text = Column(Text, nullable=True)
    reply_text = Column(Text, nullable=True)
    raw_event = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class HandoffSession(Base):
    __tablename__ = "handoff_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)
    reason = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
